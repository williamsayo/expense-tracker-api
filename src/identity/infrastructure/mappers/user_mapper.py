from datetime import datetime
from typing import cast
from uuid import UUID
from boilerplate.ports.mappers import BaseMapper
from boilerplate.domain.unique_entity_id import UniqueEntityId
from boilerplate.errors.core import CoreError
from boilerplate.errors.domain import IllegalArgumentError
from result import result_ok, result_fail, is_fail, Either, result_combine
from src.identity.domain.entities.user_entity import UserEntity
from src.identity.domain.value_objects.email_value_object import EmailValueObject
from src.identity.infrastructure.repositories.schema import UserSchema
from aiodynamo.types import Item

from src.shared.utils.type_cast import typed


def create_unique_entity_id(
    id: str | UUID,
) -> Either[UniqueEntityId, CoreError]:
    try:
        return result_ok(UniqueEntityId(id))
    except Exception as error:
        return result_fail(IllegalArgumentError(error, "Invalid User ID"))


class UserMapper(BaseMapper):
    """Maps user data between domain and persistence models."""

    @staticmethod
    def to_persistence(entity: UserEntity) -> Item:
        persistence: Item = {
            "pk": f"USER#{entity.id.to_string()}",
            "id": entity.id.to_string(),
            "username": entity.username,
            "email": entity.email.value,
            "password_hash": entity.hashed_password,
            "first_name": entity.first_name,
            "last_name": entity.last_name,
            "version": entity.version,
            "created_at": entity.created_at.isoformat(),
        }

        return cast(Item, persistence)

    @staticmethod
    def to_domain(
        persistence: Item,
    ) -> Either[UserEntity, CoreError]:
        id_result = create_unique_entity_id(persistence["id"])
        email_result = EmailValueObject.create({"value": persistence["email"]})
        combined_result = result_combine((id_result, email_result))

        if is_fail(combined_result):
            return result_fail(combined_result.value)

        entity_id, email = combined_result.value

        return UserEntity.existing_user_entity(
            {
                "email": email,
                "first_name": persistence["first_name"],
                "last_name": persistence["last_name"],
                "username": persistence["username"],
                "hashed_password": persistence["password_hash"],
                "created_at": datetime.fromisoformat(persistence["created_at"]),
            },
            id=entity_id,
            version=persistence["version"],
        )
