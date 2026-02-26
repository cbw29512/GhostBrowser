import docker
import logging
import time
from typing import Optional, Dict, Tuple
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GhostEngine")


def extract_root_domain(url: str) -> str:
    try:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        hostname = urlparse(url).hostname or ""
        parts = hostname.lower().split(".")
        return ".".join(parts[-2:]) if len(parts) >= 2 else hostname
    except Exception:
        return ""


def build_host_rules(root_domain: str) -> str:
    return (
        f"MAP * 0.0.0.0, "
        f"EXCLUDE {root_domain}, "
        f"EXCLUDE *.{root_domain}, "
        f"EXCLUDE localhost, "
        f"EXCLUDE 127.0.0.1"
    )


class ContainerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Connected to Docker Engine")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.client = None

    def _get_container_logs(self, container) -> str:
        try:
            return container.logs(tail=20).decode("utf-8", errors="replace")
        except Exception:
            return "(could not read container logs)"

    def start_browser_session(
        self,
        target_url: str,
        image: str = "selenium/standalone-chromium:latest" 
    ) -> Tuple[Optional[Dict], str]:
        if not self.client:
            return None, "Docker client not connected."

        logger.info(f"Launching Selenium container for: {target_url}")

        # --- Step 1: Clean up stale containers ---
        try:
            for c in self.client.containers.list(all=True, filters={"ancestor": image}):
                c.remove(force=True)
        except Exception:
            pass

        # --- Step 2: Launch Selenium Engine ---
        container = None
        try:
            env = {
                "SE_VNC_NO_PASSWORD": "1", 
            }

            container = self.client.containers.run(
                image=image,
                detach=True,
                shm_size="2g",
                ports={"7900/tcp": None, "4444/tcp": None},
                environment=env,
            )
            time.sleep(3)

        except Exception as e:
            logger.error(f"Container launch failed: {e}")
            return None, str(e)

        # --- Step 3: Extract Both Ports ---
        try:
            container.reload()
            if container.attrs["State"]["Status"] != "running":
                return None, "Container exited immediately."

            ports_info = container.attrs["NetworkSettings"]["Ports"]
            
            vnc_port = ports_info.get("7900/tcp")[0]["HostPort"]
            webdriver_port = ports_info.get("4444/tcp")[0]["HostPort"]
            
            logger.info(f"Container RUNNING | VNC: {vnc_port} | WebDriver: {webdriver_port}")
            
            return {
                "id": container.id, 
                "vnc_port": vnc_port, 
                "webdriver_port": webdriver_port
            }, "Success"

        except Exception as e:
            if container:
                try: container.remove(force=True)
                except: pass
            return None, f"Post-launch error: {e}"

    def wait_for_ready(self, container_id: str, timeout: int = 30) -> bool:
        if not self.client:
            return False
        try:
            container = self.client.containers.get(container_id)
            consecutive = 0
            start = time.time()
            while time.time() - start < timeout:
                container.reload()
                status = container.attrs["State"]["Status"]
                if status == "running":
                    consecutive += 1
                    if consecutive >= 2:
                        return True
                elif status in ("exited", "dead"):
                    return False
                else:
                    consecutive = 0
                time.sleep(1)
            return False
        except Exception:
            return False

    def stop_session(self, container_id: str):
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True)
            logger.info(f"Session {container_id[:12]} destroyed. All data wiped.")
        except Exception as e:
            logger.error(f"Failed to stop {container_id}: {e}")