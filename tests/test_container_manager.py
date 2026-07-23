import pytest

from ghost_browser.engine.container_manager import ContainerManager


def test_loopback_binding_is_accepted() -> None:
    ports = {
        "7900/tcp": [{"HostIp": "127.0.0.1", "HostPort": "49152"}],
    }

    assert ContainerManager._read_loopback_port(ports, "7900/tcp") == "49152"


def test_external_binding_is_rejected() -> None:
    ports = {
        "7900/tcp": [{"HostIp": "0.0.0.0", "HostPort": "49152"}],
    }

    with pytest.raises(RuntimeError, match="Unsafe host binding"):
        ContainerManager._read_loopback_port(ports, "7900/tcp")


def test_missing_binding_is_rejected() -> None:
    with pytest.raises(RuntimeError, match="No binding"):
        ContainerManager._read_loopback_port({}, "4444/tcp")
