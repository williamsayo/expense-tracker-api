from dataclasses import dataclass
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from shared.utils.setup_dependencies import BaseDependency
from shared.infrastructure.db.dependencies import get_session
from shared.utils.auth.token_verifier import TokenVerifier
from identity.infrastructure.repositories.postgres.user_repo import UserRepository

# from identity.infrastructure.repositories.local.user_repo import LocalUserRepository
from identity.infrastructure.adapters.ports.jwt_token_service import JWTTokenService
from identity.application.ports.jwt import TokenServicePort
from identity.infrastructure.repositories.base import UserRepositoryProtocol
from identity.infrastructure.services.encryption.base import EncryptionService
from identity.infrastructure.services.encryption.argon2_encrption import (
    ArgonEncryptionService,
)


def get_identity_repo(session: AsyncSession = Depends(get_session)):
    return UserRepository(session)


def get_token_service() -> TokenServicePort:
    return JWTTokenService(token_verifier=TokenVerifier())


@dataclass(slots=True, frozen=True)
class UserDependencies(BaseDependency):
    """Dependency container for user use cases."""

    repo: UserRepositoryProtocol = Depends(get_identity_repo)
    argon2_encryption_service: EncryptionService = Depends(ArgonEncryptionService)
    token_service: TokenServicePort = Depends(get_token_service)


UserDeps = Annotated[UserDependencies, Depends()]
