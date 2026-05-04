from dataclasses import dataclass, field
from uuid import UUID
from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from result import is_fail
from shared.utils.setup_dependencies import BaseDependency
from shared.utils.auth.token_verifier import TokenVerifier
from shared.domain.types.user_id import UserId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token", auto_error=False)

@dataclass(slots=True)
class AuthDependency(BaseDependency):
    """Dependency container for auth use cases."""

    token: str = Depends(oauth2_scheme)
    user_id: UserId = field(init=False)

    def __post_init__(self):
        payload_result = TokenVerifier.decode_token(self.token)
        if is_fail(payload_result):
            error = payload_result.value
            raise HTTPException(
                error.status,
                detail={"message": error.message, "error_code": error.id},
                headers={"www-authenticate": "Bearer"},
            )
        object.__setattr__(self, "user_id", UUID(payload_result.value.get("sub", None)))


AuthDeps = Annotated[AuthDependency, Depends()]
