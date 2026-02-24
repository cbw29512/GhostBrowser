import reflex as rx
from .models import VaultEntry, GhostCard
from .engine.container_manager import ContainerManager
from .security.vault_logic import VaultSecurity
from typing import List, Optional
import sqlmodel
import os

manager = ContainerManager()

class State(rx.State):
    is_vault_unlocked: bool = False
    master_password_input: str = ""
    is_browser_running: bool = False
    active_container_id: Optional[str] = None
    browser_url: str = ""
    
    # --- Secure RAM State ---
    # We do not use rx.var for the key to keep it hidden from the frontend
    vault_key: bytes = b""

    # --- New Card Form State ---
    new_site_name: str = ""
    new_site_url: str = ""

    def set_master_password_input(self, val: str):
        self.master_password_input = val

    def unlock_vault(self):
        """Derives the session key from the master password."""
        if not self.master_password_input:
            return rx.toast.error("Password required")
            
        try:
            # In a production app, we would fetch a stored salt.
            # For this masterclass, we'll use a fixed salt for the dev phase.
            dev_salt = b'ghost_salt_2026' 
            self.vault_key = VaultSecurity.derive_key(self.master_password_input, dev_salt)
            self.is_vault_unlocked = True
            return rx.toast.info("Vault Ready (RAM Key Derived)")
        except Exception as e:
            return rx.toast.error(f"Handshake failed: {e}")

    @rx.var
    def saved_cards(self) -> List[GhostCard]:
        with rx.session() as session:
            return session.exec(sqlmodel.select(GhostCard)).all()

    def add_card(self):
        if not self.new_site_name or not self.new_site_url:
            return rx.toast.error("Fields required")
            
        with rx.session() as session:
            new_card = GhostCard(
                display_name=self.new_site_name,
                target_url=self.new_site_url
            )
            session.add(new_card)
            session.commit()
            
        self.new_site_name = ""
        self.new_site_url = ""
        return rx.toast.success("Card Persistent.")

    def launch_ghost_session(self, target_site: str):
        if not self.is_vault_unlocked:
            return rx.toast.warning("Unlock vault first.")
        yield rx.toast.info(f"Launching {target_site}...")
        session = manager.start_browser_session()
        if session:
            self.active_container_id = session["id"]
            self.browser_url = f"https://localhost:{session['port']}/#/?location={target_site}"
            self.is_browser_running = True
        else:
            yield rx.toast.error("Docker failed. Check Dashboard.")

    def terminate_session(self):
        if self.active_container_id:
            manager.stop_session(self.active_container_id)
            self.active_container_id = None
            self.is_browser_running = False
            self.browser_url = ""
            return rx.toast.success("Wiped.")
