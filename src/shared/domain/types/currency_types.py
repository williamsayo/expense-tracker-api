from enum import StrEnum


class Currency(StrEnum):
    """Enumerates supported currency values."""

    USD = "USD"
    EUR = "EUR"
    NGN = "NGN"
    GHS = "GHS"


currency_display: dict[Currency, str] = {
    Currency.EUR: "€",
    Currency.GHS: "GH₵",
    Currency.NGN: "₦",
    Currency.USD: "$",
}
