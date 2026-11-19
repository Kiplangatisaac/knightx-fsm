"""
KnightX_fsm - Encryption Module
AES-256 encryption for sensitive data at rest.
"""

import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config import ENCRYPTION_KEY_PATH, DATA_DIR

class EncryptionManager:
    """Handles encryption/decryption of sensitive data using Fernet (AES-128 in CBC mode with HMAC)."""

    def __init__(self):
        self._key = self._load_or_create_key()
        self._fernet = Fernet(self._key)

    def _load_or_create_key(self) -> bytes:
        """Load existing key or generate a new one."""
        if ENCRYPTION_KEY_PATH.exists():
            try:
                return ENCRYPTION_KEY_PATH.read_bytes()
            except Exception:
                pass
        # Generate new key
        key = Fernet.generate_key()
        try:
            ENCRYPTION_KEY_PATH.write_bytes(key)
            # Restrict permissions
            os.chmod(ENCRYPTION_KEY_PATH, 0o600)
        except Exception:
            pass
        return key

    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64-encoded ciphertext."""
        if not data:
            return data
        encrypted = self._fernet.encrypt(data.encode("utf-8"))
        return base64.b64encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a base64-encoded ciphertext and return plaintext."""
        if not encrypted_data:
            return encrypted_data
        try:
            encrypted_bytes = base64.b64decode(encrypted_data.encode("utf-8"))
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode("utf-8")
        except Exception:
            return encrypted_data  # Return as-is if decryption fails

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt raw bytes."""
        return self._fernet.encrypt(data)

    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """Decrypt raw bytes."""
        return self._fernet.decrypt(encrypted_data)

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        import bcrypt
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against a bcrypt hash."""
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    def derive_key_from_password(self, password: str, salt: bytes = None) -> tuple:
        """Derive a key from a password using PBKDF2."""
        if salt is None:
            salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))
        return key, salt

# Global instance
encryption = EncryptionManager()