"""Fail before publication if tag, artifact source, contents or checksums differ."""

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("AlexaActionsWithBinaryLinux.zip", "AlexaActionsNoBinaryLinux.zip")


def prepare(tag, directory, source, commit):
    version = re.search(r"^# VERSION (\d+\.\d+\.\d+)\r?$", source, re.MULTILINE)
    if version is None or tag != "v" + version[1]:
        raise ValueError("Release tag must match the handler VERSION")
    if sorted(path.name for path in directory.glob("*.zip")) != sorted(NAMES):
        raise ValueError("Release requires exactly both tested deployment ZIPs")
    checksums = []
    for name in NAMES:
        package = directory / name
        digest = hashlib.sha256(package.read_bytes()).hexdigest()
        manifest = json.loads(package.with_suffix(".zip.json").read_text())
        if manifest["sha256"] != digest or manifest["commit"] != commit or manifest.get("dirty", True):
            raise ValueError("Package checksum or source commit differs from this tested tag")
        with zipfile.ZipFile(package) as archive:
            if archive.read("lambda_function.py").decode() != source:
                raise ValueError("Packaged handler differs from the release source")
            if "settings.json" in archive.namelist():
                raise ValueError("Public release must not contain private settings")
        checksums.append(f"{digest}  {name}")
    (directory / "SHA256SUMS").write_text("\n".join(checksums) + "\n", encoding="utf-8")


if __name__ == "__main__":
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    prepare(sys.argv[1], ROOT / "dist", (ROOT / "lambda/lambda_function.py").read_bytes().decode(), commit)
