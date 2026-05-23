from dataclasses import dataclass
from boilerplate import IEventDispatcher
from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.utils.setup_dependencies import get_cdn_service, get_object_storage
from src.shared.infrastructure.services.aws.cloudfront_service import (
    CloudFrontService,
)
from src.shared.infrastructure.adapters.ports.repository import ObjectStorageRepository
from src.shared.utils.setup_dependencies import BaseDependency
from src.shared.infrastructure.db.dependencies import get_session
from src.shared.utils.auth.token_verifier import TokenVerifier
from src.identity.infrastructure.repositories.postgres.user_repo import UserRepository
from src.identity.infrastructure.repositories.local.user_repo import LocalUserRepository
from src.identity.infrastructure.services.token.jwt_token_service import JWTTokenService
from src.identity.infrastructure.adapters.ports.token import TokenServiceProtocol
from src.identity.infrastructure.adapters.ports.repository import UserRepositoryProtocol
from src.identity.infrastructure.adapters.ports.encryption import EncryptionService
from src.identity.infrastructure.services.encryption.argon2_encrption import (
    ArgonEncryptionService,
)
from src.shared.application.events.dispatcher.dependencies import get_event_dispatcher


def get_user_repository_dependency(
    session: AsyncSession = Depends(get_session),
) -> UserRepositoryProtocol:
    """Factory function to select the appropriate UserRepository based on settings."""
    # if settings.use_local_repository:
    #     return LocalUserRepository()
    return UserRepository(session)


def get_token_service() -> TokenServiceProtocol:
    return JWTTokenService(token_verifier=TokenVerifier())


@dataclass(slots=True)
class UserDependencies(BaseDependency):
    """Dependency container for user use cases."""

    repo: UserRepositoryProtocol = Depends(get_user_repository_dependency)
    argon2_encryption_service: EncryptionService = Depends(ArgonEncryptionService)
    token_service: TokenServiceProtocol = Depends(get_token_service)
    object_storage: ObjectStorageRepository = Depends(get_object_storage)
    cdn_service: CloudFrontService = Depends(get_cdn_service)
    dispatcher:IEventDispatcher = Depends(get_event_dispatcher)

UserDeps = Annotated[UserDependencies, Depends()]
