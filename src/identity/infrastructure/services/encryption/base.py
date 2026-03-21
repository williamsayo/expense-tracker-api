from abc import ABC, abstractmethod


class EncryptionService(ABC):
    """Coordinates encryption application workflows."""

    @abstractmethod
    def hash(self, raw_password: str) -> str: ...

    @abstractmethod
    def verify(self, raw_password: str, hashed_password: str) -> bool: ...

    @abstractmethod
    def password_needs_rehash(self, hashed_password: str) -> bool: ...
