"""Block releases/merges on high or critical CodeQL security findings."""

import json
from pathlib import Path
import sys


def check(directory):
    reports = list(directory.glob("*.sarif"))
    if not reports:
        raise ValueError("CodeQL did not produce a SARIF report")
    findings = []
    for path in reports:
        runs = json.loads(path.read_text())["runs"]
        if not runs:
            raise ValueError("CodeQL report contains no analysis runs")
        for run in runs:
            rules = {rule["id"]: rule for rule in run["tool"]["driver"]["rules"]}
            for result in run.get("results", []):
                rule = rules[result["ruleId"]]
                severity = float(rule.get("properties", {}).get("security-severity", 0))
                if severity >= 7:
                    findings.append(result["ruleId"])
    if findings:
        raise ValueError(f"High/critical CodeQL security findings: {', '.join(findings)}")
    print("No high or critical CodeQL security findings")


if __name__ == "__main__":
    check(Path(sys.argv[1]))
