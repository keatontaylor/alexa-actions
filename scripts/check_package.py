"""Import the extracted deployment ZIP with no installed/site packages available."""

from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def check(path):
    with tempfile.TemporaryDirectory() as directory:
        with zipfile.ZipFile(path) as archive:
            if "lambda_function.py" not in archive.namelist():
                raise RuntimeError("Lambda handler must be at the ZIP root")
            archive.extractall(directory)
        code = (
            "import sys; sys.path.insert(0, '.'); "
            "import lambda_function, ask_sdk_core, ask_sdk_model, ask_sdk_runtime, "
            "urllib3, isodate, pydantic, typing_extensions; "
            "assert callable(lambda_function.lambda_handler); print('Isolated package import OK')"
        )
        subprocess.run([sys.executable, "-I", "-S", "-c", code], cwd=directory, check=True)


if __name__ == "__main__":
    for argument in sys.argv[1:]:
        check(Path(argument).resolve())
