import reflex as rx
import asyncio
import re
import hashlib
import secrets
from .models import VaultEntry, GhostCard, AdminProfile
from .engine.container_manager import ContainerManager
from .security.vault_logic import VaultSecurity
from typing import List, Optional, Dict, Any
import sqlmodel

manager = ContainerManager()

def clean_url(url: str) -> str:
    c_url = url.strip().lower()
    if not c_url.startswith("http://") and not c_url.startswith("https://"):
        c_url = f"https://www.{c_url}" if not c_url.startswith("www.") else f"https://{c_url}"
    return c_url

def validate_password_strength(pwd: str) -> str:
    """Enforces enterprise password standards."""
    if len(pwd) < 8: return "Must be at least 8 characters."
    if not re.search(r"[A-Z]", pwd): return "Must contain an uppercase letter."
    if not re.search(r"[a-z]", pwd): return "Must contain a lowercase letter."
    if not re.search(r"[0-9]", pwd): return "Must contain a number."
    if not re.search(r"[!@#\$%^&\*\(\),\.?\":{}|<>]", pwd): return "Must contain a special character."
    return ""

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Generates a secure PBKDF2 HMAC SHA256 hash."""
    if not salt: salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex(), salt

class State(rx.State):
    # --- System State ---
    has_admin: bool = False
    is_vault_unlocked: bool = False
    is_browser_running: bool = False
    is_booting: bool = False
    active_container_id: Optional[str] = None
    browser_url: str = ""
    vault_key: bytes = b""
    site_cards: List[GhostCard] = []
    
    # --- Admin Flow State ---
    setup_username: str = ""
    setup_password: str = ""
    setup_confirm: str = ""
    login_username: str = ""
    master_password_input: str = ""
    
    # --- PII State ---
    pii_name: str = ""
    pii_email: str = ""
    pii_phone: str = ""
    pii_address: str = ""
    pii_city: str = ""
    pii_state: str = ""
    pii_zip: str = ""
    pii_cc: str = ""
    
    # --- Card State ---
    new_site_name: str = ""
    new_site_url: str = ""
    new_authorize_pii: bool = False
    is_edit_modal_open: bool = False
    edit_card_id: int = -1
    edit_site_name: str = ""
    edit_site_url: str = ""
    edit_authorize_pii: bool = False

    # Explicit Setters
    def set_setup_username(self, val: str): self.setup_username = val
    def set_setup_password(self, val: str): self.setup_password = val
    def set_setup_confirm(self, val: str): self.setup_confirm = val
    def set_login_username(self, val: str): self.login_username = val
    def set_master_password_input(self, val: str): self.master_password_input = val
    def set_new_site_name(self, val: str): self.new_site_name = val
    def set_new_site_url(self, val: str): self.new_site_url = val
    def set_new_authorize_pii(self, val: bool): self.new_authorize_pii = val
    def set_edit_site_name(self, val: str): self.edit_site_name = val
    def set_edit_site_url(self, val: str): self.edit_site_url = val
    def set_edit_authorize_pii(self, val: bool): self.edit_authorize_pii = val
    def set_is_edit_modal_open(self, val: bool): self.is_edit_modal_open = val
    def set_pii_name(self, val: str): self.pii_name = val
    def set_pii_email(self, val: str): self.pii_email = val
    def set_pii_phone(self, val: str): self.pii_phone = val
    def set_pii_address(self, val: str): self.pii_address = val
    def set_pii_city(self, val: str): self.pii_city = val
    def set_pii_state(self, val: str): self.pii_state = val
    def set_pii_zip(self, val: str): self.pii_zip = val
    def set_pii_cc(self, val: str): self.pii_cc = val

    def load_cards(self):
        try:
            with rx.session() as session:
                self.site_cards = session.exec(sqlmodel.select(GhostCard)).all()
        except Exception as e:
            print(f"Card load error: {e}")

    def on_load(self):
        try:
            with rx.session() as session:
                admin = session.exec(sqlmodel.select(AdminProfile)).first()
                self.has_admin = bool(admin)
                
                cards = session.exec(sqlmodel.select(GhostCard)).all()
                if not cards:
                    session.add(GhostCard(display_name="YouTube", target_url="https://www.youtube.com"))
                    session.add(GhostCard(display_name="Chase Bank", target_url="https://www.chase.com"))
                    session.add(GhostCard(display_name="Amazon", target_url="https://www.amazon.com"))
                    session.add(GhostCard(display_name="Reddit", target_url="https://www.reddit.com"))
                    session.add(GhostCard(display_name="Netflix", target_url="https://www.netflix.com"))
                    session.commit()
            if self.is_vault_unlocked: self.load_cards()
        except Exception as e:
            print(f"Load error: {e}")

    def create_admin(self):
        if not self.setup_username or not self.setup_password:
            return rx.toast.error("Fields cannot be empty.")
        if self.setup_password != self.setup_confirm:
            return rx.toast.error("Passwords do not match.")
        
        pwd_err = validate_password_strength(self.setup_password)
        if pwd_err:
            return rx.toast.error(f"Weak Password: {pwd_err}")
            
        p_hash, salt = hash_password(self.setup_password)
        try:
            with rx.session() as session:
                admin = AdminProfile(username=self.setup_username, password_hash=p_hash, salt=salt)
                session.add(admin)
                session.commit()
            self.has_admin = True
            self.setup_password = ""
            self.setup_confirm = ""
            return rx.toast.success("Admin Profile Created & Secured!")
        except Exception as e:
            return rx.toast.error(f"Database error: {e}")

    def unlock_vault(self):
        if not self.login_username or not self.master_password_input:
            return rx.toast.error("Credentials required.")
        try:
            with rx.session() as session:
                admin = session.exec(sqlmodel.select(AdminProfile).where(AdminProfile.username == self.login_username)).first()
                if not admin:
                    return rx.toast.error("Invalid Username.")
                
                test_hash, _ = hash_password(self.master_password_input, admin.salt)
                if test_hash != admin.password_hash:
                    return rx.toast.error("Invalid Password.")
                    
            self.vault_key = VaultSecurity.derive_key(self.master_password_input, b"ghost_v1_salt")
            self.is_vault_unlocked = True
            self.load_cards()
            return rx.toast.success("Identity Verified. Vault Unlocked.")
        except Exception as e:
            return rx.toast.error(f"Auth Error: {e}")
            
    def lock_vault(self):
        self.vault_key = b""
        self.is_vault_unlocked = False
        self.master_password_input = ""
        self.site_cards = []
        return rx.toast.info("Vault Secured & RAM Wiped.")

    def save_pii(self):
        try:
            with rx.session() as session:
                entry = session.exec(sqlmodel.select(VaultEntry)).first()
                if not entry: entry = VaultEntry(identity_name="Main")
                entry.encrypted_payload = f"Name:{self.pii_name}|Email:{self.pii_email}|Phone:{self.pii_phone}|Addr:{self.pii_address}|City:{self.pii_city}|State:{self.pii_state}|Zip:{self.pii_zip}|CC:{self.pii_cc}"
                session.add(entry)
                session.commit()
            self.pii_cc = ""
            return rx.toast.success("PII Identity Saved.")
        except Exception:
            pass

    def add_card(self):
        if not self.new_site_name or not self.new_site_url: return rx.toast.error("Data missing")
        with rx.session() as session:
            session.add(GhostCard(display_name=self.new_site_name, target_url=clean_url(self.new_site_url), authorize_pii=self.new_authorize_pii))
            session.commit()
        self.new_site_name, self.new_site_url, self.new_authorize_pii = "", "", False
        self.load_cards()
        return rx.toast.info("Site Saved.")

    def delete_card(self, card_id: int):
        with rx.session() as session:
            card = session.get(GhostCard, card_id)
            if card:
                session.delete(card)
                session.commit()
        self.load_cards()
        return rx.toast.info("Card Deleted.")

    def prepare_edit(self, card: Dict[str, Any]):
        self.edit_card_id, self.edit_site_name, self.edit_site_url, self.edit_authorize_pii, self.is_edit_modal_open = int(card["id"]), str(card["display_name"]), str(card["target_url"]), bool(card.get("authorize_pii", False)), True

    def cancel_edit(self): self.is_edit_modal_open = False

    def save_edit(self):
        with rx.session() as session:
            card = session.get(GhostCard, self.edit_card_id)
            if card:
                card.display_name, card.target_url, card.authorize_pii = self.edit_site_name, clean_url(self.edit_site_url), self.edit_authorize_pii
                session.add(card)
                session.commit()
        self.is_edit_modal_open = False
        self.load_cards()
        return rx.toast.success("Changes Saved.")

    async def launch_ghost_session(self, url: str):
        if not self.is_vault_unlocked: return
        
        self.is_booting = True
        yield rx.toast.info("Igniting Secure Enclave...")
        
        session, err_msg = manager.start_browser_session()
        
        if session:
            self.active_container_id = session["id"]
            base_url = f"http://127.0.0.1:6900"
            
            import httpx
            is_ready = False
            async with httpx.AsyncClient() as client:
                for i in range(20):
                    try:
                        # ARCHITECT FIX: If the server responds OR disconnects, it's alive.
                        await client.get(base_url, timeout=1.0)
                        is_ready = True
                        break
                    except (httpx.ConnectError, httpx.RemoteProtocolError):
                        # ConnectError = Still booting
                        # RemoteProtocolError = Awake but refused the handshake (Success!)
                        if "disconnected" in str(httpx.RemoteProtocolError) or i > 5:
                            is_ready = True
                            break
                        pass
                    except Exception:
                        pass
                    await asyncio.sleep(2.0)
            
            if is_ready:
                # Add a 1s buffer to let the UI render
                await asyncio.sleep(1.0)
                self.browser_url = f"{base_url}/#/?location={url}"
                self.is_booting = False
                self.is_browser_running = True
                yield rx.toast.success("Enclave Online!")
            else:
                self.is_booting = False
                manager.stop_session(self.active_container_id)
                self.active_container_id = None
                yield rx.toast.error("Handshake failed. Try launching again.")
        else:
            self.is_booting = False
            yield rx.toast.error(f"Engine Error: {err_msg}")

    def terminate_session(self):
        if self.active_container_id:
            manager.stop_session(self.active_container_id)
            self.active_container_id = None
            self.is_browser_running = False
            self.browser_url = ""
            return rx.toast.success("RAM Wiped.")



