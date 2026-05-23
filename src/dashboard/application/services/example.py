from fastapi import Depends
from shared.application.services.base import BaseService

class ExampleService(BaseService):
    """Service layer."""

    def __init__(
        self,
        deps=Depends(),
    ):
        super().__init__(deps)