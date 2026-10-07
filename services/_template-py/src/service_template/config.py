"""Configuration read once, from the environment, at start-up.

CONVENTIONS: config by environment variables; secrets come from the vault through
py/listening_sdk, never from files in the repository. F6 replaces this module with the SDK's
config.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass

from service_template.log import LEVELS, Level

SERVICE = "service-template"


@dataclass(frozen=True)
class Config:
    service: str
    port: int
    log_level: Level


def load_config(env: Mapping[str, str]) -> Config:
    raw_port = env.get("PORT", "8080")
    if not re.fullmatch(r"\d+", raw_port) or int(raw_port) > 65535:
        raise ValueError(f'PORT must be a port number between 0 and 65535, got "{raw_port}"')
    level = env.get("LOG_LEVEL", "info")
    if level not in LEVELS:
        raise ValueError(f'LOG_LEVEL must be one of {", ".join(LEVELS)}, got "{level}"')
    return Config(service=SERVICE, port=int(raw_port), log_level=level)
