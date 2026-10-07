"""Entry point: health endpoints for the cluster and a clean shutdown on SIGTERM.

F6 replaces the health server with py/listening_sdk's, which also serves the Prometheus metrics
of PRD section 10.
"""

from __future__ import annotations

import os
import signal
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import FrameType
from typing import override

from service_template.config import Config, load_config
from service_template.log import Logger


class Running:
    def __init__(self, server: ThreadingHTTPServer, thread: threading.Thread, log: Logger) -> None:
        self._server = server
        self._thread = thread
        self._log = log
        self.port: int = server.server_port

    def close(self) -> None:
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()
        self._log.info("stopped")


def start(config: Config, log: Logger) -> Running:
    class Health(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # the name http.server dispatches GET requests to
            if self.path == "/healthz":
                self._reply(200, b'{"status":"ok"}')
            elif self.path == "/readyz":
                self._reply(200, b'{"ready":true}')
            else:
                self._reply(404, b"{}")

        def _reply(self, status: int, body: bytes) -> None:
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        @override
        def log_message(self, format: str, *args: object) -> None:
            return  # access logs stay out of the JSON log stream

    server = ThreadingHTTPServer(("0.0.0.0", config.port), Health)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    running = Running(server, thread, log)
    log.info("started", port=running.port)
    return running


def main() -> None:
    config = load_config(os.environ)
    log = Logger(config.service, level=config.log_level)
    running = start(config, log)
    stop = threading.Event()

    def on_signal(_signum: int, _frame: FrameType | None) -> None:
        stop.set()

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    stop.wait()
    running.close()


if __name__ == "__main__":
    main()
