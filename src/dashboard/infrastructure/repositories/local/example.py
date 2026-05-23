from typing import Sequence, Any
from boilerplate import GetAllOptions, GetOptions
from boilerplate.errors.repository import (
    ConcurrencyError,
    ConflictError,
    DataIntegrityError,
    RepositoryNotFoundError,
    RepositoryUnexpectedError,
)
from boilerplate.ports.repository import WriteRepository, ReadRepository
from boilerplate.domain.unique_entity_id import UniqueEntityId
from result import Either


class ExampleRepository(WriteRepository, ReadRepository):
    db = []

    def list(
        self, options: GetAllOptions
    ) -> Either[Sequence[Any], RepositoryUnexpectedError | DataIntegrityError]: ...

    def add(
        self, aggregate: Any
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    def get_by_id(
        self, aggregateId: UniqueEntityId
    ) -> Either[
        Any, RepositoryNotFoundError | DataIntegrityError | RepositoryUnexpectedError
    ]: ...

    def first(
        self, options: GetOptions
    ) -> Either[
        Any, RepositoryUnexpectedError | DataIntegrityError | RepositoryNotFoundError
    ]: ...

    def remove(
        self, aggregate: Any
    ) -> Either[None, RepositoryUnexpectedError | ConcurrencyError | ConflictError]: ...

    def exists(
        self, aggregateId: UniqueEntityId
    ) -> Either[bool, RepositoryUnexpectedError]: ...
