"""Sigma rule evaluation against normalised events using pysigma + field matcher."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import structlog
import yaml
from sigma.collection import SigmaCollection

from app.ingestion.fieldmap import event_to_fields
from app.ingestion.schema import NormalizedEvent
from app.services.detection.sigma_matcher import evaluate_detection

logger = structlog.get_logger(__name__)


@dataclass
class DetectionResult:
    rule_id: str
    rule_name: str
    severity: str
    confidence: float
    mitre_technique_id: str | None
    rule_type: str = "sigma"


@dataclass
class LoadedSigmaRule:
    rule_id: str
    title: str
    severity: str
    detection: dict
    mitre_technique_id: str | None
    logsource: dict


def _extract_mitre(tags: list[str]) -> str | None:
    for tag in tags:
        if tag.startswith("attack.t"):
            return tag.replace("attack.", "").upper()
    return None


def _map_level(level: str | None) -> str:
    mapping = {
        "informational": "low",
        "low": "low",
        "medium": "medium",
        "high": "high",
        "critical": "critical",
    }
    return mapping.get((level or "medium").lower(), "medium")


class SigmaEngine:
    """Load Sigma rules from disk and evaluate against NormalizedEvents."""

    def __init__(self, rules_dir: str = "data/sigma_rules"):
        self.rules: list[LoadedSigmaRule] = []
        self._load(rules_dir)

    def _load(self, rules_dir: str) -> None:
        root = Path(rules_dir)
        if not root.is_dir():
            logger.warning("sigma_rules_dir_missing", path=rules_dir)
            return

        yaml_paths = sorted(root.rglob("*.yml"))
        if not yaml_paths:
            logger.warning("sigma_rules_empty", path=rules_dir)
            return

        # Validate via pysigma
        try:
            contents = [p.read_text(encoding="utf-8") for p in yaml_paths]
            SigmaCollection.from_yaml(contents)
        except Exception as exc:
            logger.error("sigma_validation_failed", error=str(exc))
            return

        loaded = 0
        for path in yaml_paths:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
                if not data or "detection" not in data:
                    continue
                status = data.get("status")
                if status and str(status).lower() in ("experimental", "deprecated"):
                    continue

                tags = data.get("tags") or []
                if isinstance(tags, dict):
                    tags = list(tags.values())

                rule = LoadedSigmaRule(
                    rule_id=str(data.get("id") or path.stem),
                    title=data.get("title", path.stem),
                    severity=_map_level(data.get("level")),
                    detection=data["detection"],
                    mitre_technique_id=_extract_mitre(tags if isinstance(tags, list) else []),
                    logsource=data.get("logsource") or {},
                )
                if not self._matches_logsource(rule, path):
                    continue
                self.rules.append(rule)
                loaded += 1
            except Exception as exc:
                logger.warning("sigma_load_error", file=str(path), error=str(exc))

        logger.info("sigma_rules_loaded", count=loaded, dir=rules_dir)

    def _matches_logsource(self, rule: LoadedSigmaRule, path: Path) -> bool:
        """Skip rules clearly outside supported platforms."""
        product = (rule.logsource.get("product") or "").lower()
        category = (rule.logsource.get("category") or "").lower()
        path_str = str(path).lower()

        supported_products = {"", "windows", "linux", "aws", "azure", "gcp", "firewall", "sysmon"}
        if product and product not in supported_products:
            return False

        # Prefer rules in relevant directories when logsource is empty
        if not product and not category:
            relevant = (
                "windows" in path_str
                or "linux" in path_str
                or "cloud" in path_str
                or "network" in path_str
                or "sysmon" in path_str
            )
            return relevant
        return True

    def evaluate(self, event: NormalizedEvent) -> list[DetectionResult]:
        if not self.rules:
            return []

        fields = event_to_fields(event)
        results: list[DetectionResult] = []

        for rule in self.rules:
            try:
                if evaluate_detection(rule.detection, fields):
                    results.append(
                        DetectionResult(
                            rule_id=rule.rule_id,
                            rule_name=rule.title,
                            severity=rule.severity,
                            confidence=0.85,
                            mitre_technique_id=rule.mitre_technique_id,
                        )
                    )
            except Exception as exc:
                logger.debug("sigma_eval_error", rule=rule.rule_id, error=str(exc))

        return results
