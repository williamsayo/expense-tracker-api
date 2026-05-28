from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class SpendingInsightReadModel:
    total_spent: int
    total_budget: int
    period: str
