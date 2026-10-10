"""The security gate uses CodeQL rule severity, not only action completion."""

import importlib.util
import json
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "check_sarif", Path(__file__).resolve().parents[1] / "scripts/check_sarif.py"
)
sarif = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sarif)


@pytest.mark.parametrize("severity", [0, 6.9, 7, 9.8])
def test_security_severity_controls_gate(tmp_path, severity):
    report = {
        "runs": [
            {
                "tool": {
                    "driver": {"rules": [{"id": "test/rule", "properties": {"security-severity": str(severity)}}]}
                },
                "results": [{"ruleId": "test/rule"}],
            }
        ]
    }
    (tmp_path / "python.sarif").write_text(json.dumps(report))
    if severity >= 7:
        with pytest.raises(ValueError, match="High/critical"):
            sarif.check(tmp_path)
    else:
        sarif.check(tmp_path)


def test_missing_security_report_fails_closed(tmp_path):
    with pytest.raises(ValueError, match="did not produce"):
        sarif.check(tmp_path)


def test_empty_security_report_fails_closed(tmp_path):
    (tmp_path / "python.sarif").write_text('{"runs": []}')
    with pytest.raises(ValueError, match="no analysis runs"):
        sarif.check(tmp_path)
