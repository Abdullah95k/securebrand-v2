"""The service as the cluster sees it.

It starts, answers its health checks on localhost and shuts down cleanly. No network beyond the
loopback interface.
"""

import json
import urllib.error
import urllib.request

import pytest

from service_template.__main__ import start
from service_template.config import Config
from service_template.log import Logger


def get(url: str) -> tuple[int, bytes]:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def test_answers_its_health_checks_and_shuts_down_cleanly() -> None:
    lines: list[str] = []
    log = Logger("service-template", write=lines.append)
    running = start(Config(service="service-template", port=0, log_level="info"), log)
    base = f"http://127.0.0.1:{running.port}"

    assert get(f"{base}/healthz") == (200, b'{"status":"ok"}')
    assert get(f"{base}/readyz")[0] == 200
    assert get(f"{base}/nope")[0] == 404

    running.close()
    with pytest.raises(urllib.error.URLError):
        urllib.request.urlopen(f"{base}/healthz", timeout=2)
    assert [json.loads(line)["msg"] for line in lines] == ["started", "stopped"]
