import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from boilerplate.errors.repository import ConflictError
from result import is_fail, result_ok

from identity.application.services import user as user_service_module
from identity.application.services.user import UserService
from identity.domain.entities.user_entity import UserEntity
from identity.domain.value_objects.email_value_object import EmailValueObject
from identity.infrastructure.adapters.dto.user import UserUpdateModel, UserWriteModel
from shared.domain.types.user_id import UserId


def _build_user_entity() -> UserEntity:
    email_result = EmailValueObject.create({"value": "jane.doe@example.com"})
    assert not is_fail(email_result)

    entity_result = UserEntity.create(
        {
            "email": email_result.value,
            "first_name": "Jane",
            "last_name": "Doe",
            "username": "janedoe",
            "hashed_password": "hashed-password",
        }
    )
    assert not is_fail(entity_result)
    return entity_result.value


def test_create_user_usecase_hashes_password_and_persists(monkeypatch) -> None:
    class _FakeArgonEncryptionService:
        def hash(self, raw_password: str) -> str:
            return f"hashed::{raw_password}"

    monkeypatch.setattr(
        user_service_module, "ArgonEncryptionService", _FakeArgonEncryptionService
    )

    created_user = _build_user_entity()
    repo = SimpleNamespace(add=AsyncMock(return_value=result_ok(created_user)))
    deps = SimpleNamespace(
        repo=repo, argon2_encryption_service=Mock(), token_service=Mock()
    )
    service = UserService(deps)

    write_model = UserWriteModel(
        email="new.user@example.com",
        username="newuser",
        first_name="New",
        last_name="User",
        password="secret",
    )

    result = asyncio.run(service.create_user_usecase(write_model))

    assert not is_fail(result)
    added_entity = repo.add.await_args.args[0]
    assert added_entity.hashed_password == "hashed::secret"


def test_authenticate_user_usecase_rehashes_password_when_needed() -> None:
    user_entity = _build_user_entity()

    encryption_service = Mock()
    encryption_service.password_needs_rehash.return_value = True
    encryption_service.hash.return_value = "new-hash"

    token_service = Mock()
    token_service.create_access_token.return_value = result_ok("access-token")
    token_service.create_refresh_token.return_value = result_ok("refresh-token")

    repo = SimpleNamespace(
        first=AsyncMock(return_value=result_ok(user_entity)),
        add=AsyncMock(return_value=result_ok(user_entity)),
    )

    deps = SimpleNamespace(
        repo=repo,
        argon2_encryption_service=encryption_service,
        token_service=token_service,
    )
    service = UserService(deps)

    result = asyncio.run(service.authenticate_user_usecase("janedoe", "secret"))

    assert not is_fail(result)
    assert result.value["access_token"] == "access-token"
    assert result.value["refresh_token"] == "refresh-token"
    assert user_entity.hashed_password == "new-hash"
    repo.add.assert_awaited_once_with(user_entity)


def test_update_user_usecase_returns_conflict_when_username_exists() -> None:
    user_entity = _build_user_entity()

    repo = SimpleNamespace(
        get_by_id=AsyncMock(return_value=result_ok(user_entity)),
        username_exists=AsyncMock(return_value=True),
        add=AsyncMock(return_value=result_ok(user_entity)),
    )

    deps = SimpleNamespace(
        repo=repo, argon2_encryption_service=Mock(), token_service=Mock()
    )
    service = UserService(deps)

    update_model = UserUpdateModel(username="already-used")

    result = asyncio.run(
        service.update_user_usecase(UserId(user_entity.id.value), update_model)
    )

    assert is_fail(result)
    assert isinstance(result.value, ConflictError)
    repo.add.assert_not_awaited()
