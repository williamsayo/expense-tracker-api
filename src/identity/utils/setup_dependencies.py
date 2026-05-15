from dataclasses import dataclass
from fastapi import Depends
from typing import Annotated, Any
from src.shared.utils.setup_dependencies import BaseDependency
from src.shared.infrastructure.db.dependencies import get_dynamodb
from src.shared.utils.auth.token_verifier import TokenVerifier
from src.identity.infrastructure.repositories.dynamodb.user_repo import UserRepository
from src.identity.infrastructure.services.token.jwt_token_service import JWTTokenService
from src.identity.infrastructure.adapters.ports.token import TokenServiceProtocol
from src.identity.infrastructure.adapters.ports.repository import UserRepositoryProtocol
from src.identity.infrastructure.adapters.ports.encryption import EncryptionService
from src.identity.infrastructure.services.encryption.argon2_encrption import (
    ArgonEncryptionService,
)


def get_user_repository_dependency(
    dynamo_resource: Any = Depends(get_dynamodb),
) -> UserRepositoryProtocol:
    """Factory function to select the appropriate UserRepository based on settings."""
    # if settings.use_local_repository:
    #     return LocalUserRepository()
    return UserRepository(dynamo_resource)


def get_token_service() -> TokenServiceProtocol:
    return JWTTokenService(token_verifier=TokenVerifier())


@dataclass(slots=True)
class UserDependencies(BaseDependency):
    """Dependency container for user use cases."""

    repo: UserRepositoryProtocol = Depends(get_user_repository_dependency)
    argon2_encryption_service: EncryptionService = Depends(ArgonEncryptionService)
    token_service: TokenServiceProtocol = Depends(get_token_service)


UserDeps = Annotated[UserDependencies, Depends()]
