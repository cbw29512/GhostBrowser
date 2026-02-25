import docker
import logging
import time
from typing import Optional, Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GhostEngine")

class ContainerManager:
    def __init__(self):
        try:
            self.client = docker.from_env()
            logger.info("Connected to Docker Engine")
        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.client = None

    def start_browser_session(self, image: str = "kasmweb/chromium:1.15.0") -> Tuple[Optional[Dict], str]:
        if not self.client: 
            return None, "Docker client not connected."
            
        try:
            # Clean up old containers to free the port
            for c in self.client.containers.list(all=True, filters={"ancestor": image}):
                c.remove(force=True)
                
            container = self.client.containers.run(
                image=image,
                detach=True,
                shm_size='512m', 
                # ARCHITECT FIX: Switch to 6900 (HTTP). No SSL certs means no browser warnings!
                ports={'6900/tcp': 6900}, 
                environment={"VNC_PW": "ghost_pass"},
            )
            
            return {"id": container.id, "port": 6900}, "Success"
                
        except Exception as e:
            logger.error(f"Launch failed: {e}")
            return None, str(e)

    def stop_session(self, container_id: str):
        try:
            container = self.client.containers.get(container_id)
            container.remove(force=True)
        except Exception as e:
            logger.error(f"Failed to stop: {e}")
