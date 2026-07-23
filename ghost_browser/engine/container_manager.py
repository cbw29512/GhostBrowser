import logging
import os
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse

import docker
from docker.errors import DockerException, NotFound

logger = logging.getLogger("GhostEngine")

MANAGED_LABEL = "ghost-browser-managed"
DEFAULT_IMAGE = "selenium/standalone-chromium:latest"
LOCAL_BIND_ADDRESS = "127.0.0.1"


def extract_root_domain(url: str) -> str:
    """Return a safe hostname for logging without paths, queries, or credentials."""
    try:
        normalized = url if url.startswith(("http://", "https://")) else f"https://{url}"
        hostname = urlparse(normalized).hostname or "unknown"
        parts = hostname.lower().split(".")
        return ".".join(parts[-2:]) if len(parts) >= 2 else hostname
    except (TypeError, ValueError):
        return "unknown"


class ContainerManager:
    """Create and destroy short-lived, loopback-only Selenium containers."""

    def __init__(self) -> None:
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info("Connected to Docker Engine")
        except DockerException:
            logger.exception("Failed to connect to Docker Engine")
            self.client = None

    def _remove_stale_managed_containers(self) -> None:
        """Remove only containers created by this application."""
        if not self.client:
            return

        try:
            containers = self.client.containers.list(
                all=True,
                filters={"label": f"{MANAGED_LABEL}=true"},
            )
            for container in containers:
                container.remove(force=True)
        except DockerException:
            logger.exception("Failed to remove stale GhostBrowser containers")

    @staticmethod
    def _read_loopback_port(ports_info: Dict, container_port: str) -> str:
        """Return a published port only when Docker bound it to loopback."""
        bindings = ports_info.get(container_port) or []
        if not bindings:
            raise RuntimeError(f"No binding found for {container_port}")

        binding = bindings[0]
        host_ip = binding.get("HostIp")
        host_port = binding.get("HostPort")
        if host_ip not in {LOCAL_BIND_ADDRESS, "::1"} or not host_port:
            raise RuntimeError(f"Unsafe host binding for {container_port}: {host_ip}:{host_port}")
        return str(host_port)

    def start_browser_session(
        self,
        target_url: str,
        image: Optional[str] = None,
    ) -> Tuple[Optional[Dict[str, str]], str]:
        """Start Selenium with no externally reachable VNC or WebDriver port."""
        if not self.client:
            return None, "Docker client is unavailable."

        selected_image = image or os.getenv("GHOST_BROWSER_IMAGE", DEFAULT_IMAGE)
        logger.info("Launching isolated browser for domain: %s", extract_root_domain(target_url))
        self._remove_stale_managed_containers()

        container = None
        try:
            container = self.client.containers.run(
                image=selected_image,
                detach=True,
                shm_size="2g",
                ports={
                    "7900/tcp": (LOCAL_BIND_ADDRESS, None),
                    "4444/tcp": (LOCAL_BIND_ADDRESS, None),
                },
                environment={"SE_VNC_NO_PASSWORD": "1"},
                labels={MANAGED_LABEL: "true"},
                security_opt=["no-new-privileges:true"],
                cap_drop=["ALL"],
                pids_limit=512,
            )
            time.sleep(3)
            container.reload()

            if container.attrs["State"]["Status"] != "running":
                raise RuntimeError("Container exited immediately")

            ports_info = container.attrs["NetworkSettings"]["Ports"]
            vnc_port = self._read_loopback_port(ports_info, "7900/tcp")
            webdriver_port = self._read_loopback_port(ports_info, "4444/tcp")

            logger.info("Container ready with loopback-only published ports")
            return {
                "id": container.id,
                "vnc_port": vnc_port,
                "webdriver_port": webdriver_port,
            }, "Success"
        except (DockerException, RuntimeError, KeyError, IndexError, TypeError):
            logger.exception("Container launch or validation failed")
            if container is not None:
                try:
                    container.remove(force=True)
                except DockerException:
                    logger.exception("Failed to clean up rejected container")
            return None, "Secure browser container failed to start."

    def wait_for_ready(self, container_id: str, timeout: int = 30) -> bool:
        if not self.client:
            return False

        try:
            container = self.client.containers.get(container_id)
            consecutive_running_checks = 0
            started_at = time.monotonic()

            while time.monotonic() - started_at < timeout:
                container.reload()
                status = container.attrs["State"]["Status"]
                if status == "running":
                    consecutive_running_checks += 1
                    if consecutive_running_checks >= 2:
                        return True
                elif status in {"exited", "dead"}:
                    return False
                else:
                    consecutive_running_checks = 0
                time.sleep(1)
            return False
        except (DockerException, KeyError, NotFound):
            logger.exception("Container readiness check failed")
            return False

    def stop_session(self, container_id: str) -> None:
        if not self.client:
            return

        try:
            container = self.client.containers.get(container_id)
            if container.labels.get(MANAGED_LABEL) != "true":
                logger.error("Refusing to remove unmanaged container %s", container_id[:12])
                return
            container.remove(force=True)
            logger.info("Destroyed managed browser session %s", container_id[:12])
        except NotFound:
            logger.info("Browser session already absent: %s", container_id[:12])
        except DockerException:
            logger.exception("Failed to stop browser session %s", container_id[:12])
