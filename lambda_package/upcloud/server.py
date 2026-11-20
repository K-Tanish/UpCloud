"""A dependency-free local HTTP server for the UpCloud demo dashboard."""

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse

from upcloud.service import get_dashboard, get_findings, run_demo_scan

_STATIC_DIR = Path(__file__).parent / "static"
_STATIC_FILES = {
    "/static/app.css": _STATIC_DIR / "app.css",
    "/static/app.js": _STATIC_DIR / "app.js",
}
_MAX_REQUEST_BYTES = 16_384


class UpCloudHandler(BaseHTTPRequestHandler):
    """Serve the dashboard and its small JSON API."""

    server_version = "UpCloudDemo/1.0"

    def do_GET(self) -> None:
        request = urlparse(self.path)
        if request.path == "/":
            self._send_file(_STATIC_DIR / "index.html")
            return
        if request.path in _STATIC_FILES:
            self._send_file(_STATIC_FILES[request.path])
            return

        params = parse_qs(request.query, keep_blank_values=True)
        provider = self._query_value(params, "provider", "all")
        category = self._query_value(params, "category", "hygiene")
        try:
            if request.path == "/api/health":
                self._send_json(200, {"status": "ok", "mode": "simulation"})
            elif request.path == "/api/dashboard":
                self._send_json(200, get_dashboard(provider, category))
            elif request.path == "/api/findings":
                findings = get_findings(
                    provider,
                    category,
                    risk=self._query_value(params, "risk", ""),
                    query=self._query_value(params, "q", ""),
                )
                self._send_json(200, {"findings": findings, "total": len(findings)})
            else:
                self._send_json(404, {"error": "Not found"})
        except ValueError as error:
            self._send_json(400, {"error": str(error)})

    def do_POST(self) -> None:
        request = urlparse(self.path)
        if request.path != "/api/scan":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            payload = self._read_json_body()
            provider = payload.get("provider", "all")
            category = payload.get("category", "hygiene")
            if not isinstance(provider, str) or not isinstance(category, str):
                raise ValueError("provider and category must be strings")
            self._send_json(200, run_demo_scan(provider, category))
        except (ValueError, json.JSONDecodeError) as error:
            self._send_json(400, {"error": str(error)})

    def _read_json_body(self) -> Dict[str, Any]:
        content_length = self.headers.get("Content-Length", "0")
        try:
            length = int(content_length)
        except ValueError as error:
            raise ValueError("Content-Length must be a valid integer") from error
        if length < 0 or length > _MAX_REQUEST_BYTES:
            raise ValueError("Request body is too large")
        if length == 0:
            return {}
        try:
            payload = json.loads(self.rfile.read(length))
        except json.JSONDecodeError as error:
            raise ValueError("Request body must contain valid JSON") from error
        if not isinstance(payload, dict):
            raise ValueError("Request body must be a JSON object")
        return payload

    @staticmethod
    def _query_value(params: Dict[str, list], key: str, default: str) -> str:
        values = params.get(key)
        return values[0] if values else default

    def _send_file(self, path: Path) -> None:
        try:
            content = path.read_bytes()
        except OSError:
            self._send_json(500, {"error": "Dashboard asset could not be read"})
            return
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: int, body: Dict[str, Any]) -> None:
        content = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format_string: str, *args: Any) -> None:
        print(f"UpCloud: {format_string % args}")


def main(argv: Optional[list] = None) -> None:
    parser = argparse.ArgumentParser(description="Run the local UpCloud demo dashboard.")
    parser.add_argument("--host", default="127.0.0.1", help="Address to bind (default: localhost)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), UpCloudHandler)
    print(f"UpCloud demo is running at http://{args.host}:{args.port}")
    print("Simulation only: no cloud credentials or cloud API calls are used.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping UpCloud demo.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
