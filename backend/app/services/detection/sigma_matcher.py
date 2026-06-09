"""Sigma detection condition evaluator for streaming events."""

from __future__ import annotations

import re
from typing import Any

from app.ingestion.fieldmap import resolve_field


def _parse_field_key(key: str) -> tuple[str, list[str]]:
    if "|" in key:
        field, mods = key.split("|", 1)
        return field, [m.strip() for m in mods.split("|")]
    return key, []


def _as_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return " ".join(str(v) for v in value)
    return str(value)


def _match_value(field_value: Any, expected: Any, modifiers: list[str]) -> bool:
    if field_value is None:
        return False

    expected_list = expected if isinstance(expected, list) else [expected]

    for exp in expected_list:
        exp_str = _as_str(exp)
        val_str = _as_str(field_value)

        if not modifiers:
            if val_str == exp_str:
                return True
            continue

        matched = False
        for mod in modifiers:
            mod_lower = mod.lower()
            if mod_lower in ("contains", "contains|all"):
                matched = exp_str.lower() in val_str.lower()
            elif mod_lower == "startswith":
                matched = val_str.lower().startswith(exp_str.lower())
            elif mod_lower == "endswith":
                matched = val_str.lower().endswith(exp_str.lower())
            elif mod_lower == "re":
                matched = bool(re.search(exp_str, val_str, re.IGNORECASE))
            elif mod_lower in ("gt",):
                try:
                    matched = float(val_str) > float(exp_str)
                except ValueError:
                    matched = False
            elif mod_lower in ("gte",):
                try:
                    matched = float(val_str) >= float(exp_str)
                except ValueError:
                    matched = False
            elif mod_lower in ("lt",):
                try:
                    matched = float(val_str) < float(exp_str)
                except ValueError:
                    matched = False
            elif mod_lower in ("lte",):
                try:
                    matched = float(val_str) <= float(exp_str)
                except ValueError:
                    matched = False
            else:
                # all, cidr, etc. – fall back to equality
                matched = val_str == exp_str

            if not matched:
                break

        if matched:
            return True

    return False


def _match_selection(selection: dict[str, Any], fields: dict[str, Any]) -> bool:
    """All field predicates in a selection must match (AND)."""
    for key, expected in selection.items():
        if key == "condition":
            continue
        if key.startswith("filter"):
            continue
        field_name, modifiers = _parse_field_key(key)
        value = resolve_field(fields, field_name)
        if not _match_value(value, expected, modifiers):
            return False
    return True


def _eval_identifier(name: str, detection: dict[str, Any], fields: dict[str, Any]) -> bool:
    block = detection.get(name)
    if block is None:
        return False
    if isinstance(block, dict):
        return _match_selection(block, fields)
    return False


def _tokenize_condition(condition: str) -> list[str]:
    """Tokenise a Sigma condition string."""
    tokens: list[str] = []
    current = ""
    i = 0
    while i < len(condition):
        ch = condition[i]
        if ch in " \t":
            if current:
                tokens.append(current)
                current = ""
            i += 1
            continue
        if condition[i : i + 3] == "and":
            if current:
                tokens.append(current)
                current = ""
            tokens.append("and")
            i += 3
            continue
        if condition[i : i + 2] == "or":
            if current:
                tokens.append(current)
                current = ""
            tokens.append("or")
            i += 2
            continue
        if condition[i : i + 3] == "not":
            if current:
                tokens.append(current)
                current = ""
            tokens.append("not")
            i += 3
            continue
        if condition[i : i + 2] == "1 " and condition[i : i + 4] == "1 of":
            if current:
                tokens.append(current)
                current = ""
            tokens.append("1of")
            i += 4
            continue
        if condition[i : i + 3] == "all" and condition[i : i + 6] == "all of":
            if current:
                tokens.append(current)
                current = ""
            tokens.append("allof")
            i += 6
            continue
        current += ch
        i += 1
    if current:
        tokens.append(current)
    return tokens


def _eval_condition(condition: str, detection: dict[str, Any], fields: dict[str, Any]) -> bool:
    """Evaluate a Sigma condition expression."""
    condition = condition.strip()

    # 1 of them*
    if condition.startswith("1 of "):
        pattern = condition[5:].strip()
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            matches = [
                _eval_identifier(k, detection, fields)
                for k in detection
                if k.startswith(prefix) and k != "condition"
            ]
            return any(matches)
        return _eval_identifier(pattern, detection, fields)

    # all of them*
    if condition.startswith("all of "):
        pattern = condition[7:].strip()
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            keys = [k for k in detection if k.startswith(prefix) and k != "condition"]
            return bool(keys) and all(_eval_identifier(k, detection, fields) for k in keys)
        return _eval_identifier(pattern, detection, fields)

    # Simple: selection
    if condition in detection:
        return _eval_identifier(condition, detection, fields)

    # Parse compound: a and b, a and not b, a or b
    tokens = _tokenize_condition(condition)
    if not tokens:
        return False

    result: bool | None = None
    negate_next = False
    op: str | None = None

    for token in tokens:
        if token == "not":
            negate_next = True
            continue
        if token in ("and", "or"):
            op = token
            continue
        if token in ("1of", "allof"):
            continue

        val = _eval_identifier(token, detection, fields)
        if negate_next:
            val = not val
            negate_next = False

        if result is None:
            result = val
        elif op == "and":
            result = result and val
        elif op == "or":
            result = result or val
        op = None

    return bool(result)


def evaluate_detection(detection: dict[str, Any], fields: dict[str, Any]) -> bool:
    """Return True if the event fields satisfy the Sigma detection block."""
    condition = detection.get("condition")
    if not condition:
        return False
    return _eval_condition(str(condition), detection, fields)
