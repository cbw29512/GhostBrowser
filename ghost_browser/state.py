import asyncio
import hashlib
import json
import logging
import os
import re
import secrets
import subprocess
import threading
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import reflex as rx
import sqlmodel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from .engine.container_manager import ContainerManager
from .models import AdminProfile, GhostCard, VaultEntry
from .security.vault_logic import VaultSecurity

logger = logging.getLogger("GhostState")
manager = ContainerManager()


def clean_url(url: str) -> str:
    """Normalize a user URL and permit only ordinary HTTP(S) destinations."""
    candidate = str(url or "").strip()
    if not candidate:
        raise ValueError("A destination URL is required")
    if not candidate.startswith(("http://", "https://")):
        candidate = f"https://{candidate}"

    parsed = urlparse(candidate)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("Only valid HTTP or HTTPS URLs are allowed")
    if parsed.username or parsed.password:
        raise ValueError("Credentials must not be embedded in a URL")
    if any(ord(character) < 32 for character in candidate):
        raise ValueError("URL contains invalid control characters")

    return parsed._replace(fragment="").geturl()


def validate_password_strength(password: str) -> str:
    if len(password) < 12:
        return "Must be at least 12 characters."
    if not re.search(r"[A-Z]", password):
        return "Must contain an uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Must contain a lowercase letter."
    if not re.search(r"[0-9]", password):
        return "Must contain a number."
    if not re.search(r"[!@#\$%^&\*\(\),\.?\":{}|<>]", password):
        return "Must contain a special character."
    return ""


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """Preserve the existing admin-password format for backward compatibility."""
    selected_salt = salt or secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        selected_salt.encode("utf-8"),
        100_000,
    )
    return key.hex(), selected_salt


class State(rx.State):
    """Frontend-safe state with secrets held only in underscore-prefixed vars."""

    has_admin: bool = False
    is_vault_unlocked: bool = False
    is_browser_running: bool = False
    is_booting: bool = False
    browser_url: str = ""
    active_domain: str = ""
    site_cards: List[GhostCard] = []

    # Reflex backend-only vars are not synchronized to the browser.
    _vault_key: str = ""
    _active_container_id: Optional[str] = None

    setup_username: str = ""
    setup_password: str = ""
    setup_confirm: str = ""
    login_username: str = ""
    master_password_input: str = ""

    pii_name: str = ""
    pii_email: str = ""
    pii_phone: str = ""
    pii_address: str = ""
    pii_city: str = ""
    pii_state: str = ""
    pii_zip: str = ""
    pii_cc: str = ""

    new_site_name: str = ""
    new_site_url: str = ""
    new_authorize_pii: bool = False
    is_edit_modal_open: bool = False
    edit_card_id: int = -1
    edit_site_name: str = ""
    edit_site_url: str = ""
    edit_authorize_pii: bool = False

    def set_setup_username(self, val: str):
        self.setup_username = val

    def set_setup_password(self, val: str):
        self.setup_password = val

    def set_setup_confirm(self, val: str):
        self.setup_confirm = val

    def set_login_username(self, val: str):
        self.login_username = val

    def set_master_password_input(self, val: str):
        self.master_password_input = val

    def set_new_site_name(self, val: str):
        self.new_site_name = val

    def set_new_site_url(self, val: str):
        self.new_site_url = val

    def set_new_authorize_pii(self, val: bool):
        self.new_authorize_pii = val

    def set_edit_site_name(self, val: str):
        self.edit_site_name = val

    def set_edit_site_url(self, val: str):
        self.edit_site_url = val

    def set_edit_authorize_pii(self, val: bool):
        self.edit_authorize_pii = val

    def set_is_edit_modal_open(self, val: bool):
        self.is_edit_modal_open = val

    def set_pii_name(self, val: str):
        self.pii_name = val

    def set_pii_email(self, val: str):
        self.pii_email = val

    def set_pii_phone(self, val: str):
        self.pii_phone = val

    def set_pii_address(self, val: str):
        self.pii_address = val

    def set_pii_city(self, val: str):
        self.pii_city = val

    def set_pii_state(self, val: str):
        self.pii_state = val

    def set_pii_zip(self, val: str):
        self.pii_zip = val

    def set_pii_cc(self, val: str):
        self.pii_cc = val

    def _require_unlocked(self) -> bool:
        return self.is_vault_unlocked and bool(self._vault_key)

    def _load_cards(self) -> None:
        if not self._require_unlocked():
            self.site_cards = []
            return
        try:
            with rx.session() as session:
                self.site_cards = list(session.exec(sqlmodel.select(GhostCard)).all())
        except Exception:
            logger.exception("Card load failed")
            self.site_cards = []

    @staticmethod
    def _vault_salt(admin_salt: str) -> bytes:
        """Domain-separate the vault KDF from the existing login hash salt."""
        return hashlib.sha256(f"ghost-vault-v2:{admin_salt}".encode("utf-8")).digest()

    def _migrate_legacy_payload(
        self,
        session: Any,
        entry: Optional[VaultEntry],
        password: str,
        new_key_hex: str,
    ) -> None:
        """Re-encrypt a v1 payload after the first successful v2 login."""
        if entry is None or not entry.encrypted_payload:
            return

        try:
            VaultSecurity.decrypt_data(entry.encrypted_payload, new_key_hex)
            return
        except ValueError:
            logger.info("Current vault key did not decrypt payload; checking legacy format")

        legacy_key_hex = VaultSecurity.derive_legacy_key(password).hex()
        plaintext = VaultSecurity.decrypt_data(entry.encrypted_payload, legacy_key_hex)
        entry.encrypted_payload = VaultSecurity.encrypt_data(plaintext, new_key_hex)
        session.add(entry)
        session.commit()
        logger.info("Migrated legacy vault payload to the per-admin v2 KDF")

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
            if self._require_unlocked():
                self._load_cards()
        except Exception:
            logger.exception("Initial state load failed")

    def create_admin(self):
        if not self.setup_username or not self.setup_password:
            return rx.toast.error("Fields cannot be empty.")
        if self.setup_password != self.setup_confirm:
            return rx.toast.error("Passwords do not match.")

        password_error = validate_password_strength(self.setup_password)
        if password_error:
            return rx.toast.error(f"Weak password: {password_error}")

        password_hash, salt = hash_password(self.setup_password)
        try:
            with rx.session() as session:
                if session.exec(sqlmodel.select(AdminProfile)).first():
                    self.has_admin = True
                    return rx.toast.error("An admin profile already exists.")
                session.add(
                    AdminProfile(
                        username=self.setup_username.strip(),
                        password_hash=password_hash,
                        salt=salt,
                    )
                )
                session.commit()
            self.has_admin = True
            return rx.toast.success("Admin profile created.")
        except Exception:
            logger.exception("Admin profile creation failed")
            return rx.toast.error("Admin profile could not be created.")
        finally:
            self.setup_password = ""
            self.setup_confirm = ""

    def unlock_vault(self):
        if not self.login_username or not self.master_password_input:
            return rx.toast.error("Credentials required.")

        password = self.master_password_input
        self.master_password_input = ""
        try:
            with rx.session() as session:
                admin = session.exec(
                    sqlmodel.select(AdminProfile).where(
                        AdminProfile.username == self.login_username.strip()
                    )
                ).first()
                if not admin:
                    return rx.toast.error("Invalid credentials.")

                test_hash, _ = hash_password(password, admin.salt)
                if not secrets.compare_digest(test_hash, admin.password_hash):
                    return rx.toast.error("Invalid credentials.")

                new_key_hex = VaultSecurity.derive_key(
                    password,
                    self._vault_salt(admin.salt),
                ).hex()
                entry = session.exec(sqlmodel.select(VaultEntry)).first()
                self._migrate_legacy_payload(session, entry, password, new_key_hex)

            self._vault_key = new_key_hex
            self.is_vault_unlocked = True
            self._load_cards()
            return rx.toast.success("Identity verified. Vault unlocked.")
        except ValueError:
            logger.exception("Vault authentication or migration failed")
            self._vault_key = ""
            self.is_vault_unlocked = False
            return rx.toast.error("Vault could not be unlocked.")
        except Exception:
            logger.exception("Unexpected vault unlock failure")
            self._vault_key = ""
            self.is_vault_unlocked = False
            return rx.toast.error("Vault could not be unlocked.")

    def lock_vault(self):
        if self._active_container_id:
            manager.stop_session(self._active_container_id)
        self._active_container_id = None
        self._vault_key = ""
        self.is_vault_unlocked = False
        self.is_browser_running = False
        self.master_password_input = ""
        self.browser_url = ""
        self.active_domain = ""
        self.site_cards = []
        self.pii_cc = ""
        return rx.toast.info("Vault locked and browser session destroyed.")

    def save_pii(self):
        if not self._require_unlocked():
            return rx.toast.error("Vault must be unlocked to save identity data.")

        try:
            card_digits = re.sub(r"\D", "", self.pii_cc)
            payload = {
                "name": self.pii_name.strip(),
                "email": self.pii_email.strip(),
                "phone": self.pii_phone.strip(),
                "address": self.pii_address.strip(),
                "city": self.pii_city.strip(),
                "state": self.pii_state.strip(),
                "zip": self.pii_zip.strip(),
                # Never retain a full payment-card number in this local vault.
                "card_last4": card_digits[-4:] if card_digits else "",
            }
            encrypted_payload = VaultSecurity.encrypt_data(
                json.dumps(payload, separators=(",", ":")),
                self._vault_key,
            )
            with rx.session() as session:
                entry = session.exec(sqlmodel.select(VaultEntry)).first()
                if entry is None:
                    entry = VaultEntry(identity_name="Main")
                entry.encrypted_payload = encrypted_payload
                session.add(entry)
                session.commit()

            self.pii_cc = ""
            return rx.toast.success("Identity data encrypted; only the card last four were retained.")
        except Exception:
            logger.exception("Identity data save failed")
            self.pii_cc = ""
            return rx.toast.error("Identity data could not be saved.")

    def add_card(self):
        if not self._require_unlocked():
            return rx.toast.error("Unlock the vault first.")
        if not self.new_site_name or not self.new_site_url:
            return rx.toast.error("Site name and URL are required.")

        try:
            target_url = clean_url(self.new_site_url)
            with rx.session() as session:
                session.add(
                    GhostCard(
                        display_name=self.new_site_name.strip(),
                        target_url=target_url,
                        authorize_pii=self.new_authorize_pii,
                    )
                )
                session.commit()
            self.new_site_name = ""
            self.new_site_url = ""
            self.new_authorize_pii = False
            self._load_cards()
            return rx.toast.info("Site saved.")
        except ValueError as exc:
            return rx.toast.error(str(exc))
        except Exception:
            logger.exception("Site-card creation failed")
            return rx.toast.error("Site could not be saved.")

    def delete_card(self, card_id: int):
        if not self._require_unlocked():
            return rx.toast.error("Unlock the vault first.")
        try:
            with rx.session() as session:
                card = session.get(GhostCard, card_id)
                if card:
                    session.delete(card)
                    session.commit()
            self._load_cards()
            return rx.toast.info("Site deleted.")
        except Exception:
            logger.exception("Site-card deletion failed")
            return rx.toast.error("Site could not be deleted.")

    def prepare_edit(self, card: Dict[str, Any]):
        if not self._require_unlocked():
            return rx.toast.error("Unlock the vault first.")
        self.edit_card_id = int(card["id"])
        self.edit_site_name = str(card["display_name"])
        self.edit_site_url = str(card["target_url"])
        self.edit_authorize_pii = bool(card.get("authorize_pii", False))
        self.is_edit_modal_open = True

    def cancel_edit(self):
        self.is_edit_modal_open = False

    def save_edit(self):
        if not self._require_unlocked():
            return rx.toast.error("Unlock the vault first.")
        try:
            target_url = clean_url(self.edit_site_url)
            with rx.session() as session:
                card = session.get(GhostCard, self.edit_card_id)
                if card:
                    card.display_name = self.edit_site_name.strip()
                    card.target_url = target_url
                    card.authorize_pii = self.edit_authorize_pii
                    session.add(card)
                    session.commit()
            self.is_edit_modal_open = False
            self._load_cards()
            return rx.toast.success("Changes saved.")
        except ValueError as exc:
            return rx.toast.error(str(exc))
        except Exception:
            logger.exception("Site-card update failed")
            return rx.toast.error("Changes could not be saved.")

    async def launch_ghost_session(self, url: str):
        if not self._require_unlocked():
            yield rx.toast.error("Unlock the vault first.")
            return

        try:
            target_url = clean_url(url)
        except ValueError as exc:
            yield rx.toast.error(str(exc))
            return

        self.is_booting = True
        yield rx.toast.info("Starting isolated browser...")

        event_loop = asyncio.get_event_loop()
        session_info, error_message = await event_loop.run_in_executor(
            None,
            lambda: manager.start_browser_session(target_url),
        )
        if not session_info:
            self.is_booting = False
            logger.error("Secure browser launch rejected: %s", error_message)
            yield rx.toast.error("Secure browser failed to start.")
            return

        self._active_container_id = session_info["id"]
        vnc_port = session_info["vnc_port"]
        webdriver_port = session_info["webdriver_port"]

        is_ready = await event_loop.run_in_executor(
            None,
            lambda: manager.wait_for_ready(self._active_container_id, timeout=30),
        )
        if not is_ready:
            self.is_booting = False
            manager.stop_session(self._active_container_id)
            self._active_container_id = None
            yield rx.toast.error("Secure browser stopped unexpectedly.")
            return

        yield rx.toast.info("Connecting to the browser engine...")
        await asyncio.sleep(2.0)

        try:
            def open_browser():
                chrome_options = Options()
                chrome_options.add_argument("--kiosk")
                chrome_options.add_argument("--disable-infobars")
                driver = webdriver.Remote(
                    command_executor=f"http://127.0.0.1:{webdriver_port}/wd/hub",
                    options=chrome_options,
                )
                driver.get(target_url)
                return driver

            await event_loop.run_in_executor(None, open_browser)
        except Exception:
            logger.exception("WebDriver connection failed")
            if self._active_container_id:
                manager.stop_session(self._active_container_id)
            self._active_container_id = None
            self.is_booting = False
            yield rx.toast.error("Secure browser connection failed.")
            return

        parsed_host = urlparse(target_url).hostname or target_url
        parts = parsed_host.split(".")
        self.active_domain = ".".join(parts[-2:]) if len(parts) >= 2 else parsed_host
        self.browser_url = (
            f"http://127.0.0.1:{vnc_port}/vnc_lite.html"
            "?autoconnect=true&resize=scale"
        )
        self.is_booting = False
        self.is_browser_running = True
        yield rx.toast.success("Isolated browser is online.")

    def terminate_session(self):
        if self._active_container_id:
            manager.stop_session(self._active_container_id)
        self._active_container_id = None
        self.is_browser_running = False
        self.browser_url = ""
        self.active_domain = ""
        return rx.toast.success("Browser session destroyed.")

    def pop_out_session(self):
        if not self.browser_url:
            return rx.toast.error("No active session to open.")

        browser_url = self.browser_url

        def spawn_secure_window():
            temp_profile = os.path.join(
                os.environ.get("TEMP", ""),
                f"ghost_popout_profile_{secrets.token_hex(8)}",
            )
            flags = [
                f"--app={browser_url}",
                f"--user-data-dir={temp_profile}",
                "--window-size=1280,720",
            ]
            browser_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            ]
            browser_executable = next(
                (path for path in browser_paths if os.path.exists(path)),
                None,
            )
            if not browser_executable:
                logger.error("No supported local browser executable was found")
                return
            try:
                subprocess.Popen([browser_executable, *flags])
            except OSError:
                logger.exception("Failed to open isolated browser window")

        threading.Thread(target=spawn_secure_window, daemon=True).start()
        return rx.toast.success("Browser detached to a separate window.")
