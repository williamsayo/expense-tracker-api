from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from src.core.config import get_settings
from src.identity.infrastructure.adapters.ports.encryption import EncryptionService

settings = get_settings()

class ArgonEncryptionService(EncryptionService):
    """Coordinates argon encryption application workflows."""

    encryption = PasswordHasher(
        time_cost=settings.time_cost,
        memory_cost=settings.memory_cost,
        parallelism=settings.parallelism,
        hash_len=settings.salt_len,
        salt_len=settings.salt_len,
        encoding="utf-8",
    )

    def hash(self, raw_password: str) -> str:
        return ArgonEncryptionService.encryption.hash(raw_password)

    def verify(self, raw_password: str, hashed_password: str) -> bool:
        try:
            return ArgonEncryptionService.encryption.verify(
                hashed_password, raw_password
            )
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    def password_needs_rehash(self, hashed_password: str) -> bool:
        """
        Check if a stored hash was made with outdated parameters.
        If True, re-hash the password on next successful login.
        """
        return ArgonEncryptionService.encryption.check_needs_rehash(hashed_password)
