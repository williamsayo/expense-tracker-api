from datetime import datetime
from typing import TypedDict, Self, Never, NotRequired
from boilerplate.domain.aggregate_root import AggregateRoot
from boilerplate.domain.unique_entity_id import UniqueEntityId
from result import result_ok, Either
from src.identity.domain.events.user_created import UserCreated
from src.identity.domain.value_objects.email_value_object import EmailValueObject


class UserEntityProps(TypedDict):
    """Typed dictionary for user entity fields."""

    first_name: str | None
    last_name: str | None
    email: EmailValueObject
    hashed_password: str
    username: str
    created_at: NotRequired[datetime]
    avatar: str | None


class UserEntity(AggregateRoot[UserEntityProps]):
    """Aggregate root for user."""

    def __init__(
        self,
        props: UserEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ):
        super().__init__(props, id, version)

    @property
    def first_name(self) -> str | None:
        self._check_is_discarded_entity()
        return self.props["first_name"]

    @property
    def last_name(self) -> str | None:
        self._check_is_discarded_entity()
        return self.props["last_name"]

    @property
    def email(self) -> EmailValueObject:
        self._check_is_discarded_entity()
        return self.props["email"]

    @property
    def username(self) -> str:
        self._check_is_discarded_entity()
        return self.props["username"]

    @property
    def hashed_password(self) -> str:
        self._check_is_discarded_entity()
        return self.props["hashed_password"]

    @property
    def avatar(self) -> str | None:
        self._check_is_discarded_entity()
        return self.props["avatar"]

    @property
    def created_at(self) -> datetime:
        self._check_is_discarded_entity()
        return self.props.get("created_at", datetime.now())

    def set_new_hash(self, new_hash: str) -> None:
        self._check_is_discarded_entity()
        self.props["hashed_password"] = new_hash

    def update_user(
        self,
        firstname: str | None,
        lastname: str | None,
        username: str | None,
        *,
        avatar: str | None = None,
    ) -> None:
        self._check_is_discarded_entity()

        self._change_name(firstname, lastname)
        self._change_username(username)

        if avatar is not None:
            self.update_avatar(avatar)

        self._increment_version()

    def _change_name(self, first_name: str | None, last_name: str | None) -> None:
        if first_name is not None:
            self.props["first_name"] = first_name
        if last_name is not None:
            self.props["last_name"] = last_name

    def _change_username(self, username: str | None) -> None:
        if username is not None:
            self.props["username"] = username

    def update_avatar(self, avatar_url: str) -> None:
        self._check_is_discarded_entity()
        self.props["avatar"] = avatar_url

    def change_password(self, new_hashed_password: str) -> None:
        self._check_is_discarded_entity()
        self.props["hashed_password"] = new_hashed_password

    @classmethod
    def create(
        cls,
        props: UserEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ) -> Either[Self, Never]:
        entity = cls(props, id, version)
        entity.apply(
            UserCreated.create_event(
                {
                    "user_id": entity.id.to_string(),
                    "email": entity.email.value,
                },
                metadata={
                    "aggregate_type": cls.__name__,
                    "version": entity.version,
                },
            )
        )
        return result_ok(entity)

    @classmethod
    def existing_user_entity(
        cls, props: UserEntityProps, id: UniqueEntityId, version: int
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))