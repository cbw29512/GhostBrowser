import docker
import logging
from typing import Optional, Dict

# Set up meaningful logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GhostEngine")

class ContainerManager:
    def __init__(self):
        try:
            # Connect to Docker Desktop on Windows
            self.client = docker.from_env()
            logger.info("Connected to Docker Engine")
        except Exception as e:
            logger.error(f"Failed to connect to Docker: {e}")
            self.client = None

    def start_browser_session(self, image: str = "kasmweb/chromium:1.15.0") -> Optional[Dict]:
        """
        Spins up a fresh browser container.
        Uses tmpfs for zero-persistence on disk.
        """
        if not self.client:
            return None

        try:
            # Senior Architect Rule: Always use try/except for resource allocation
            container = self.client.containers.run(
                image=image,
                detach=True,
                # Map browser profile to RAM only
                tmpfs={'/home/kasm-default-profile': ''},
                ports={'6901/tcp': None}, # Auto-assign a random high port
                environment={"VNC_PW": "ghost_pass"},
            )
            
            # Refresh object to get assigned ports
            container.reload()
            host_port = container.attrs['NetworkSettings']['Ports']['6901/tcp'][0]['HostPort']
            
            return {
                "id": container.id,
                "port": host_port
            }
        except Exception as e:
            logger.error(f"Container launch failed: {e}")
            return None

    def stop_session(self, container_id: str):
        """Kills and removes the container instantly."""
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True)
            logger.info(f"Session {container_id[:12]} destroyed.")
        except Exception as e:
            logger.error(f"Failed to stop container {container_id}: {e}")
