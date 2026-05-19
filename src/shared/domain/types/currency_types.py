from enum import StrEnum


class Currency(StrEnum):
    """Enumerates supported currency values."""

    USD = "USD"
    EUR = "EUR"
    NGN = "NGN"
    GHS = "GHS"
    GBP = "GBP"


currency_symbols: dict[Currency, str] = {
    Currency.EUR: "€",
    Currency.GHS: "GH₵",
    Currency.NGN: "₦",
    Currency.USD: "$",
    Currency.GBP: "£",
}

CURRENCY_FACTORS = {
    Currency.EUR: 100,
    Currency.GHS: 100,
    Currency.NGN: 100,
    Currency.USD: 100,
    Currency.GBP: 100,
}
