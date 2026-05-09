from uuid import uuid4
import jwt
from result import result_fail, result_ok, Either
from boilerplate.errors.http import AuthorizationError
from boilerplate.errors.error_ids import ApplicationErrorID
from src.core.config import settings
from src.shared.utils.auth.token_payload import TokenPayload


class TokenVerifier:
    """Validates token values."""

    @staticmethod
    def decode_token(token: str) -> Either[TokenPayload, AuthorizationError]:
        try:
            decoded = jwt.decode(
                jwt=token,
                key=settings.secret_key.get_secret_value(),
                algorithms=[settings.jwt_algorithm],
                options={"require": ["exp", "sub"]},
            )
            payload = TokenPayload(**decoded)
            return result_ok(payload)
        except jwt.ExpiredSignatureError as error:
            return result_fail(
                AuthorizationError(
                    ApplicationErrorID.AUTHORIZATION, "Expired user token"
                )
            )
        except jwt.InvalidTokenError as error:
            return result_fail(
                AuthorizationError(
                    ApplicationErrorID.AUTHORIZATION, "Invalid user token passed"
                )
            )
