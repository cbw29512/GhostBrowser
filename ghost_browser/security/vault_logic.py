import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class VaultSecurity:
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """Derives a 32-byte key from a password and salt."""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))

    @staticmethod
    def encrypt_data(data: str, key: bytes) -> str:
        """Encrypts a string using the derived key."""
        f = Fernet(key)
        return f.encrypt(data.encode()).decode()

    @staticmethod
    def decrypt_data(token: str, key: bytes) -> str:
        """Decrypts a token using the derived key."""
        f = Fernet(key)
        return f.decrypt(token.encode()).decode()
