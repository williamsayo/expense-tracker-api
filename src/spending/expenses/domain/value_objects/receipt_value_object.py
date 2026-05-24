from typing import Self, TypedDict
from boilerplate import ValueObject, DomainRuleError, apply_rules
from result import is_fail, result_ok, result_fail, Either
from src.shared.application.dtos.upload import FileUploadDTO
from src.shared.infrastructure.adapters.ports.cdn import CDNService


class ReceiptValueObjectProps(TypedDict):
    """Typed dictionary for receipt value object fields."""

    receipt_key: str | None


class ReceiptValueObject(ValueObject[ReceiptValueObjectProps]):
    """
    Value Object
    """

    def __init__(self, props: ReceiptValueObjectProps):
        super().__init__(props)
        self.url = None

    @property
    def key(self) -> str | None:
        return self.props["receipt_key"]

    @property
    def receipt(self) -> str | None:
        return self.url

    @property
    def has_receipt(self) -> bool:
        return self.receipt is not None

    @classmethod
    def create(cls, props: ReceiptValueObjectProps) -> Either[Self, DomainRuleError]:
        return result_ok(cls(props))

    def to_url(self, key: str | None, cdn: CDNService) -> str | None:
        if key is not None:
            self.url = cdn.generate_url(key)

        return self.url