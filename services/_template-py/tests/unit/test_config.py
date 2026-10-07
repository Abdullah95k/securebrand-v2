import dataclasses

import pytest

from service_template.config import Config, load_config


def test_reads_the_port_and_the_log_level_from_the_environment_with_defaults() -> None:
    assert load_config({}) == Config(service="service-template", port=8080, log_level="info")
    assert load_config({"PORT": "9100", "LOG_LEVEL": "debug"}).port == 9100


def test_config_is_frozen_so_it_is_read_once_and_never_changed() -> None:
    config = load_config({})
    with pytest.raises(dataclasses.FrozenInstanceError):
        config.port = 1  # type: ignore[misc]


@pytest.mark.parametrize("port", ["http", "70000", "-1"])
def test_rejects_a_port_that_is_not_a_port_number(port: str) -> None:
    with pytest.raises(ValueError, match="PORT"):
        load_config({"PORT": port})


def test_rejects_an_unknown_log_level() -> None:
    with pytest.raises(ValueError, match="LOG_LEVEL"):
        load_config({"LOG_LEVEL": "verbose"})
