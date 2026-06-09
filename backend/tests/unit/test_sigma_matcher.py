"""Tests for Sigma detection condition evaluator."""

from app.services.detection.sigma_matcher import evaluate_detection


def test_simple_selection_match():
    detection = {
        "selection": {
            "Image|endswith": "mimikatz.exe",
        },
        "condition": "selection",
    }
    fields = {"Image": "C:\\Tools\\mimikatz.exe"}
    assert evaluate_detection(detection, fields)


def test_selection_no_match():
    detection = {
        "selection": {"CommandLine|contains": "invoke-mimikatz"},
        "condition": "selection",
    }
    fields = {"CommandLine": "whoami"}
    assert not evaluate_detection(detection, fields)


def test_and_condition():
    detection = {
        "selection": {
            "Image|endswith": "cmd.exe",
            "CommandLine|contains": "whoami",
        },
        "condition": "selection",
    }
    fields = {"Image": "cmd.exe", "CommandLine": "whoami /all"}
    assert evaluate_detection(detection, fields)


def test_one_of_pattern():
    detection = {
        "selection_a": {"Image|endswith": "cmd.exe"},
        "selection_b": {"Image|endswith": "powershell.exe"},
        "condition": "1 of selection_*",
    }
    fields = {"Image": "powershell.exe"}
    assert evaluate_detection(detection, fields)
