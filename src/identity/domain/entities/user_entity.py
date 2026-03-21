from typing import TypedDict, Self, Never
from boilerplate.domain.aggregate_root import AggregateRoot
from boilerplate.domain.unique_entity_id import UniqueEntityId
from result import result_ok, Either
from identity.domain.value_objects.email_value_object import EmailValueObject


class UserEntityProps(TypedDict):
    """Typed dictionary for user entity fields."""

    first_name: str
    last_name: str
    email: EmailValueObject
    hashed_password: str
    username: str


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
    def first_name(self) -> str:
        self._check_is_discarded_entity()
        return self.props["first_name"]

    @property
    def last_name(self) -> str:
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

    def set_new_hash(self, new_hash: str) -> None:
        self._check_is_discarded_entity()
        self.props["hashed_password"] = new_hash

    def update_user(
        self, firstname: str | None, lastname: str | None, username: str | None
    ) -> None:
        self._check_is_discarded_entity()
        if firstname is not None:
            self.props["first_name"] = firstname
        if lastname is not None:
            self.props["last_name"] = lastname
        if username is not None:
            self.props["username"] = username
        self._increment_version()

    @classmethod
    def create(
        cls,
        props: UserEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))

    @classmethod
    def existing_user_entity(
        cls, props: UserEntityProps, id: UniqueEntityId, version: int
    ) -> Either[Self, Never]:
        return result_ok(cls(props, id, version))
