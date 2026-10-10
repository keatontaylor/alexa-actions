"""Guard the hosted runtime's import boundary without requiring an Amazon account."""

from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.skipif(sys.version_info >= (3, 10), reason="Legacy TLS compatibility applies to the hosted runtime")
def test_handler_import_with_hosted_openssl_metadata():
    # Simulate the reported hosted OpenSSL version. This verifies import guards,
    # not TLS handshakes with the real legacy OpenSSL library.
    code = (
        "import ssl; "
        "ssl.OPENSSL_VERSION = 'OpenSSL 1.0.2k-fips  26 Jan 2017'; "
        "ssl.OPENSSL_VERSION_INFO = (1, 0, 2, 11, 15); "
        "import sys; sys.path.insert(0, '.'); "
        "import lambda_function; "
        "assert callable(lambda_function.lambda_handler)"
    )
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[1] / "lambda",
        check=True,
    )
