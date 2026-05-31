from typing import Protocol
from boilerplate import IEventDispatcher
from src.spending.budgeting.infrastructure.adapters.ports.repository import BudgetReadRepositoryProtocol, BudgetRepositoryProtocol


class BudgetCommandDeps(Protocol):
    """Protocol defining the dependencies required by budget command use cases."""

    repo: BudgetRepositoryProtocol
    dispatcher: IEventDispatcher


class BudgetQueryDeps(Protocol):
    """Protocol defining the dependencies required by budget query use cases."""

    repo: BudgetReadRepositoryProtocol