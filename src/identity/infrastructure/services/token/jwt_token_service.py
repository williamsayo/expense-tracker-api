import json
from uuid import uuid4
from typing import Never
from datetime import datetime, timedelta, timezone
import jwt
import hashlib
import hmac
from result import result_fail, result_ok, Either, is_fail, result_combine
from boilerplate.errors.http import AuthorizationError
from boilerplate.errors.application import UnexpectedError
from boilerplate.errors.error_ids import ApplicationErrorID
from src.core.config import settings
from src.identity.infrastructure.adapters.dto.token import (
    Token,
    TokenPayload,
)
from src.shared.utils.auth.token_verifier import TokenVerifier


class JWTTokenService:
    """Handles JWT token generation and validation."""

    def __init__(self, token_verifier: TokenVerifier):
        self.token_verifier = token_verifier

    def generate_token(
        self,
        user_id: str,
        token_type: Token,
        exp: timedelta,
        jti: str | None = None,
    ) -> Either[str, TypeError]:
        try:
            payload: TokenPayload = {
                "sub": user_id,
                "token_type": token_type,
                "jti": jti or str(uuid4()),
                "exp": (exp + datetime.now(timezone.utc)).timestamp(),
            }
            token = jwt.encode(
                payload={**payload},
                key=settings.secret_key.get_secret_value(),
                algorithm=settings.jwt_algorithm,
            )
            return result_ok(token)
        except TypeError as error:
            return result_fail(error)

    def create_access_token(
        self, user_id: str, expiry: timedelta = timedelta(seconds=240)
    ) -> Either[str, UnexpectedError]:
        result = self.generate_token(
            user_id=user_id,
            token_type=Token.ACCESS,
            exp=expiry,
        )
        if is_fail(result):
            return result_fail(UnexpectedError(result.value))
        return result

    def hash_token_id(self, jti: str) -> Either[str, Never]:
        hash = hmac.new(
            settings.secret_key.get_secret_value().encode(),
            jti.encode(),
            hashlib.sha256,
        ).hexdigest()
        return result_ok(hash)

    def generate_refresh_key(self, jti: str) -> Either[str, Never]:
        hash = self.hash_token_id(jti)
        return result_ok(f"refresh:{hash.value}")

    def verify_refresh_token(
        self, token: str
    ) -> Either[str, AuthorizationError | UnexpectedError]:
        payload_result = self.token_verifier.decode_token(token)

        if is_fail(payload_result):
            return payload_result

        payload = payload_result.value

        if payload.get("token_type") != Token.REFRESH.value:
            return result_fail(
                AuthorizationError(
                    ApplicationErrorID.AUTHORIZATION, "Invalid user token passed"
                )
            )

        access_token = self.create_access_token(payload.get("sub"))

        if is_fail(access_token):
            return access_token

        return result_ok(access_token.value)

    def create_refresh_token(
        self,
        user_id: str,
        expiry: timedelta = timedelta(days=7),
    ) -> Either[str, UnexpectedError]:
        jti: str = str(uuid4())
        refresh_token_result = self.generate_token(
            user_id=user_id, jti=jti, token_type=Token.REFRESH, exp=expiry
        )
        refresh_key_result = self.generate_refresh_key(jti)
        result = result_combine((refresh_token_result, refresh_key_result))

        if is_fail(result):
            return result_fail(UnexpectedError(result.value))

        token, key = result.value

        return result_ok(token)

    def serialize(self, data: dict) -> str:
        return json.dumps(data)

    def deserialize(self, data: str) -> dict:
        return json.loads(data)
