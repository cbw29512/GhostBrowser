import reflex as rx
from .models import VaultEntry, GhostCard
from typing import List, Optional

class State(rx.State):
    """The central state manager for Ghost Browser."""
    
    # --- Vault State ---
    is_vault_unlocked: bool = False
    master_password_input: str = ""
    
    # --- Session State ---
    is_browser_running: bool = False
    active_container_id: Optional[str] = None
    selected_url: str = ""

    def unlock_vault(self):
        """
        Verify master password. 
        Note: For Phase 1, we use a 'hardcoded' admin check.
        Phase 3 will upgrade this to Argon2 hashing.
        """
        try:
            if self.master_password_input == "admin":
                self.is_vault_unlocked = True
                return rx.toast.info("Vault Unlocked")
            else:
                return rx.toast.error("Invalid Master Password")
        except Exception as e:
            # Error-First: Log the failure
            print(f"Error during unlock: {e}")
            return rx.toast.error("System Error during unlock")

    def launch_ghost_session(self, url: str):
        """Prepares the state for the container engine."""
        if not self.is_vault_unlocked:
            return rx.toast.warning("Unlock vault to proceed.")
        
        self.selected_url = url
        self.is_browser_running = True
        # Logic for engine/container_manager will be called here in Phase 2
