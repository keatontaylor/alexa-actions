"""Publish pytest results to the job summary, including on a failed test run."""

import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET


def summarize(directory):
    lines = ["### SDK and HTTP/TLS tests", ""]
    junit = directory / "junit.xml"
    if junit.exists():
        suite = ET.parse(junit).getroot().find("testsuite")
        lines.append(
            "Tests: {tests}; failures: {failures}; errors: {errors}; skipped: {skipped}.".format(**suite.attrib)
        )
    else:
        lines.append("No test report produced. Check dependency installation and test output.")
    coverage = directory / "coverage.json"
    if coverage.exists():
        total = json.loads(coverage.read_text())["totals"]
        lines += ["", f"Statement and branch coverage: {total['percent_covered']:.2f}% (required: 85%)."]
    summary = "\n".join(lines) + "\n"
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as output:
            output.write(summary)
    print(summary)


if __name__ == "__main__":
    summarize(Path(sys.argv[1]))
