"""Lightweight HTTP API server for Homepage dashboard integration.

Starts a background thread that serves JSON on GET /api/status.
Configure the port with the RANGARR_API_PORT environment variable (default 7474).
"""

import json
import logging
import os
import threading
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from rangarr.stats import stats

logger = logging.getLogger(__name__)

_DEFAULT_PORT = 7474


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path in ('/api/status', '/api/status/'):
            body = json.dumps(stats.snapshot(), indent=2).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        logger.debug(f'API: {format % args}')


def start_api_server() -> None:
    """Start the API HTTP server in a daemon thread."""
    port = int(os.environ.get('RANGARR_API_PORT', _DEFAULT_PORT))
    server = HTTPServer(('0.0.0.0', port), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name='rangarr-api')
    thread.start()
    logger.info(f'API server started on port {port} — GET /api/status')
