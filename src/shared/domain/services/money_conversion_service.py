from decimal import Decimal
from boilerplate import DomainRuleError
from result import Either, result_fail
from src.shared.domain.value_objects.money_value_object import MoneyValueObject
from src.shared.domain.types.currency_types import Currency


class FxProtocol:
    async def get_rates(self, currency: str) -> dict[str, float]: ...


class MoneyConversionService:

    def __init__(self, fx: FxProtocol) -> None:
        self.fx = fx

    async def covert(
        self,
        money: MoneyValueObject,
        target_currency: Currency,
    ) -> Either[MoneyValueObject, DomainRuleError]:
        rates = await self.fx.get_rates(money.currency)
        rate = rates.get(target_currency)

        if rate is None:
            return result_fail(DomainRuleError(Exception("Cannot convert to currency")))

        return MoneyValueObject.create(
            {"amount": round(rate * money.amount), "currency": target_currency}
        )
