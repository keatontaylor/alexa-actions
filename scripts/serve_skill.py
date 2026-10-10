"""Simulation-only HTTP adapter for the unmodified handler inside a deployment ZIP.

Run with python -I -S: dependencies must come entirely from the ZIP. This is
an ASK request-envelope adapter, not an Amazon service or Lambda runtime emulator.
"""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import zipfile


def serve(package):
    with tempfile.TemporaryDirectory() as directory:
        with zipfile.ZipFile(package) as archive:
            archive.extractall(directory)
        os.chdir(directory)
        sys.path.insert(0, directory)
        import lambda_function

        lock = threading.Lock()

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                # Avoid logging entire request envelopes, questions or test tokens.
                pass

            def do_GET(self):
                self.send_response(200 if self.path == "/health" else 404)
                self.end_headers()

            def do_POST(self):
                if self.path != "/invoke":
                    self.send_error(404)
                    return
                event = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                with lock:
                    result = lambda_function.lambda_handler(event, None)
                body = json.dumps(result).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        print("Packaged ASK handler ready", flush=True)
        ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()


if __name__ == "__main__":
    serve(Path(sys.argv[1]).resolve())
