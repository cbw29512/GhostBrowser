import base64
import hashlib
import re
import secrets
from typing import Optional

from cryptography.fernet import Fernet, InvalidToken


class VaultSecurity:
    """Password validation, key derivation, and authenticated encryption helpers."""

    CURRENT_KDF_ITERATIONS = 600_000
    LEGACY_KDF_ITERATIONS = 100_000

    @staticmethod
    def validate_secure_password(password: str) -> bool:
        """Require a reasonably strong local vault password."""
        if len(password) < 12:
            return False
        if not re.search(r"[A-Z]", password):
            return False
        if not re.search(r"[a-z]", password):
            return False
        if not re.search(r"[0-9]", password):
            return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False
        return True

    @staticmethod
    def hash_admin_credentials(
        password: str,
        salt: Optional[str] = None,
        iterations: int = CURRENT_KDF_ITERATIONS,
    ) -> tuple[str, str]:
        """Hash an admin password with PBKDF2-SHA256 and a random salt."""
        selected_salt = salt or secrets.token_hex(32)
        key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            selected_salt.encode("utf-8"),
            iterations,
        )
        return key.hex(), selected_salt

    @staticmethod
    def derive_key(
        password: str,
        salt: bytes,
        iterations: int = CURRENT_KDF_ITERATIONS,
    ) -> bytes:
        """Derive the 32-byte raw key required by Fernet."""
        if not password:
            raise ValueError("Password is required")
        if len(salt) < 16:
            raise ValueError("KDF salt must be at least 16 bytes")
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=32,
        )

    @classmethod
    def derive_legacy_key(cls, password: str) -> bytes:
        """Derive the original v1 key only for one-time payload migration."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            b"ghost_v1_salt",
            cls.LEGACY_KDF_ITERATIONS,
            dklen=32,
        )

    @staticmethod
    def _build_fernet(key_hex: str) -> Fernet:
        """Convert a 32-byte hexadecimal key into a Fernet instance."""
        try:
            key_bytes = bytes.fromhex(key_hex)
        except (TypeError, ValueError) as exc:
            raise ValueError("Vault key is malformed") from exc

        if len(key_bytes) != 32:
            raise ValueError("Vault key must be exactly 32 bytes")
        return Fernet(base64.urlsafe_b64encode(key_bytes))

    @classmethod
    def encrypt_data(cls, data: str, key_hex: str) -> str:
        """Encrypt and authenticate UTF-8 plaintext with Fernet."""
        if not isinstance(data, str):
            raise TypeError("Vault plaintext must be a string")
        return cls._build_fernet(key_hex).encrypt(data.encode("utf-8")).decode("utf-8")

    @classmethod
    def decrypt_data(cls, token: str, key_hex: str) -> str:
        """Decrypt a Fernet token and normalize authentication failures."""
        try:
            plaintext = cls._build_fernet(key_hex).decrypt(token.encode("utf-8"))
            return plaintext.decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Vault authentication failed") from exc
        except UnicodeError as exc:
            raise ValueError("Vault payload is not valid UTF-8") from exc
