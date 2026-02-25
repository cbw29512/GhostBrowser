import hashlib
import secrets
import re

class VaultSecurity:
    @staticmethod
    def validate_secure_password(password: str) -> bool:
        """
        Enforces standard secure password requirements:
        - 8+ characters
        - 1 Uppercase, 1 Lowercase
        - 1 Number
        - 1 Special character
        """
        if len(password) < 8: return False
        if not re.search(r"[A-Z]", password): return False
        if not re.search(r"[a-z]", password): return False
        if not re.search(r"[0-9]", password): return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): return False
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
        """Used for deriving the RAM encryption key for PII data."""
        return hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)[:32]
