from typing import Self, TypedDict
from boilerplate import ValueObject, DomainRuleError, apply_rules
from result import is_fail, result_ok, result_fail, Either
from src.shared.domain.rules.media_rule import MediaSchema
from src.shared.infrastructure.adapters.ports.cdn import CDNService


class MediaValueObjectProps(TypedDict):
    """Typed dictionary for media value object fields."""

    file_key: str | None
    file_url: str | None


class MediaValueObject(ValueObject[MediaValueObjectProps]):
    """
    Value Object
    """

    def __init__(self, props: MediaValueObjectProps):
        super().__init__(props)

    @property
    def key(self) -> str | None:
        return self.props["file_key"]

    @property
    def url(self) -> str | None:
        return self.props["file_url"]

    @property
    def has_file(self) -> bool:
        return self.key is not None

    @classmethod
    def create(cls, props: MediaValueObjectProps) -> Either[Self, DomainRuleError]:
        result = apply_rules(props, MediaSchema)

        if is_fail(result):
            return result_fail(
                DomainRuleError(result.value, "Invalid media properties")
            )

        return result_ok(cls(result.value))

    def update_url(
        self, cdn: CDNService
    ) -> Either["MediaValueObject", DomainRuleError]:
        if self.key is not None:
            result = MediaValueObject.create(
                {"file_key": self.key, "file_url": cdn.generate_url(self.key)}
            )
            if is_fail(result):
                return result

            return result

        return result_ok(self)
