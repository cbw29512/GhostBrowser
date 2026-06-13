import hashlib
import secrets
import base64
import re
from cryptography.fernet import Fernet, InvalidToken


class VaultSecurity:
    @staticmethod
    def validate_secure_password(password: str) -> bool:
        """
        Enforces standard secure password requirements:
        - 8+ characters, 1 Uppercase, 1 Lowercase, 1 Number, 1 Special character
        """
        if len(password) < 8: return False
        if not re.search(r"[A-Z]", password): return False
        if not re.search(r"[a-z]", password): return False
        if not re.search(r"[0-9]", password): return False
        if not re.search(r"[!@#$%^&*(),.?\\\":{}|<>]", password): return False
        return True

    @staticmethod
    def hash_admin_credentials(password: str, salt: str = None):
        """Salts and hashes a password using PBKDF2-SHA256."""
        if salt is None:
            salt = secrets.token_hex(16)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        )
        return key.hex(), salt

    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derives a 32-byte raw key used for AES Fernet encryption."""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)[:32]

    @staticmethod
    def _build_fernet(key_hex: str) -> Fernet:
        """Internal: converts 32-byte hex key to a Fernet cipher instance."""
        key_bytes = bytes.fromhex(key_hex)
        fernet_key = base64.urlsafe_b64encode(key_bytes)
        return Fernet(fernet_key)

    @staticmethod
    def encrypt_data(data: str, key_hex: str) -> str:
        """Encrypts plaintext using AES-128 CBC (Fernet). Returns base64 token."""
        f = VaultSecurity._build_fernet(key_hex)
        return f.encrypt(data.encode('utf-8')).decode('utf-8')

    @staticmethod
    def decrypt_data(token: str, key_hex: str) -> str:
        """Decrypts a Fernet token. Raises InvalidToken on wrong key or tampering."""
        try:
            f = VaultSecurity._build_fernet(key_hex)
            return f.decrypt(token.encode('utf-8')).decode('utf-8')
        except InvalidToken:
            raise ValueError("Decryption failed: invalid token or wrong key")
