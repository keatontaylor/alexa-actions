"""Publication must fail closed for mismatched or contaminated artifacts."""

import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

spec = importlib.util.spec_from_file_location(
    "prepare_release", Path(__file__).resolve().parents[1] / "scripts/prepare_release.py"
)
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
SOURCE = "# VERSION 1.2.3\n"
COMMIT = "a" * 40


@pytest.fixture
def packages(tmp_path):
    for name in release.NAMES:
        path = tmp_path / name
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("lambda_function.py", SOURCE)
        path.with_suffix(".zip.json").write_text(
            json.dumps({"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "commit": COMMIT, "dirty": False})
        )
    return tmp_path


def test_release_checksums_match_both_tested_artifacts(packages):
    release.prepare("v1.2.3", packages, SOURCE, COMMIT)
    assert (packages / "SHA256SUMS").read_text().splitlines() == [
        f"{hashlib.sha256((packages / name).read_bytes()).hexdigest()}  {name}" for name in release.NAMES
    ]


@pytest.mark.parametrize("tag", ["v1.2.4", "1.2.3", "v1.2.3-rc1", "invalid"])
def test_release_rejects_wrong_version(packages, tag):
    with pytest.raises(ValueError, match="tag"):
        release.prepare(tag, packages, SOURCE, COMMIT)
    assert not (packages / "SHA256SUMS").exists()


@pytest.mark.parametrize("key,value", [("sha256", "wrong"), ("commit", "other_source"), ("dirty", True)])
def test_release_rejects_tampered_or_wrong_source_artifacts(packages, key, value):
    path = (packages / release.NAMES[0]).with_suffix(".zip.json")
    manifest = json.loads(path.read_text())
    manifest[key] = value
    path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="checksum or source"):
        release.prepare("v1.2.3", packages, SOURCE, COMMIT)


@pytest.mark.parametrize("private", [False, True])
def test_release_rejects_wrong_handler_or_private_settings(packages, private):
    path = packages / release.NAMES[0]
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("lambda_function.py", SOURCE if private else "different source")
        if private:
            archive.writestr("settings.json", '{"TOKEN":"public-test-placeholder"}')
    path.with_suffix(".zip.json").write_text(
        json.dumps({"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "commit": COMMIT, "dirty": False})
    )
    with pytest.raises(ValueError, match="private settings" if private else "handler differs"):
        release.prepare("v1.2.3", packages, SOURCE, COMMIT)


def test_release_requires_both_packages(packages):
    (packages / release.NAMES[0]).unlink()
    with pytest.raises(ValueError, match="both"):
        release.prepare("v1.2.3", packages, SOURCE, COMMIT)
