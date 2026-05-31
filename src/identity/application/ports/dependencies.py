from typing_extensions import Protocol
from boilerplate import IEventDispatcher
from src.identity.infrastructure.adapters.ports.encryption import EncryptionService
from src.identity.infrastructure.adapters.ports.repository import UserRepositoryProtocol
from src.identity.infrastructure.adapters.ports.token import TokenServiceProtocol
from src.shared.infrastructure.adapters.ports.repository import ObjectStorageRepository
from src.shared.infrastructure.services.aws.cloudfront_service import CloudFrontService


class IdentityDependencies(Protocol):
    """Protocol defining the dependencies required by user use cases."""

    repo: UserRepositoryProtocol
    argon2_encryption_service: EncryptionService
    token_service: TokenServiceProtocol
    object_storage: ObjectStorageRepository
    cdn_service: CloudFrontService
    dispatcher: IEventDispatcher
