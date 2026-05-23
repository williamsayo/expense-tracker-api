from typing import TypedDict, Self
from boilerplate.domain.aggregate_root import AggregateRoot
from boilerplate.domain.unique_entity_id import UniqueEntityId

class ExampleEntityProps(TypedDict): ...

class ExampleEntity(AggregateRoot[ExampleEntityProps]):
    """
    class for domain entity.

    An entity is defined primarily by its identity (id). Two entities with the 
    same attributes but different ids are considered distinct.

    Attributes:
        id (uuid.UUID): Unique identifier for the entity.
    """
    def __init__(
        self,
        props: ExampleEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ):
        super().__init__(props, id, version)

    @classmethod
    def create(
        cls,
        props: ExampleEntityProps,
        id: UniqueEntityId | None = None,
        version: int = 0,
    ) -> Self:
        return cls(props, id, version)

    @classmethod
    def existing_entity(
        cls, props: ExampleEntityProps, id: UniqueEntityId, version: int
    ) -> Self:
        return cls(props, id, version)
