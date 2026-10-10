"""Build complete Lambda ZIPs without changing the source directory."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
NAMES = {"binary": "AlexaActionsWithBinaryLinux.zip", "pure": "AlexaActionsNoBinaryLinux.zip"}


def build(kind, output):
    if sys.version_info[:2] != (3, 13):
        raise RuntimeError("Build release packages with Python 3.13 to match deployment dependencies")
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        staging = Path(directory) / "package"
        command = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--target",
            str(staging),
            "-r",
            str(ROOT / "lambda" / "requirements.txt"),
        ]
        environment = os.environ.copy()
        if kind == "binary":
            # Match the self-managed Lambda runtime and architecture, even on Windows/macOS.
            command += [
                "--platform",
                "manylinux2014_x86_64",
                "--implementation",
                "cp",
                "--python-version",
                "3.13",
                "--only-binary=:all:",
            ]
        else:
            # Pydantic v1 supports a pure Python build; do not accidentally compile host binaries.
            command += ["--no-binary=pydantic,charset_normalizer"]
            environment["SKIP_CYTHON"] = "1"
        subprocess.run(command, check=True, env=environment)
        for source in (ROOT / "lambda").iterdir():
            if source.suffix in {".py", ".json", ".txt"}:
                shutil.copy2(source, staging / source.name)
        destination = output / NAMES[kind]
        with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
            for source in sorted(staging.rglob("*")):
                if not source.is_file() or "__pycache__" in source.parts or source.suffix == ".pyc":
                    continue
                if kind == "pure" and source.suffix in {".so", ".pyd", ".dll"}:
                    raise RuntimeError(f"Unexpected native library in pure package: {source.name}")
                archive.write(source, source.relative_to(staging))
        distributions = subprocess.check_output(
            [sys.executable, "-m", "pip", "list", "--path", str(staging), "--format=json"], text=True
        )
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        manifest = {
            "commit": commit,
            "dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()),
            "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
            "kind": kind,
            "python": "3.13",
            "architecture": "x86_64" if kind == "binary" else "pure-python",
            "dependencies": json.loads(distributions),
        }
        destination.with_suffix(".zip.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(destination)
        return destination


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--kind", choices=NAMES, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    build(args.kind, args.output.resolve())
