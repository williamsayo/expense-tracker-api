import logging
from typing import Callable, Coroutine, Any
from fastapi.responses import Response
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from boilerplate.errors.application import ApplicationError
from boilerplate.errors.domain import DomainError
from boilerplate.errors.repository import (
    RepositoryError,
    RepositoryNotFoundError,
    DataIntegrityError,
    ConcurrencyError,
    ConflictError,
)
from boilerplate.errors.http import (
    AuthenticationError,
    AuthorizationError,
    BadGatewayError,
    BadRequestError,
    NotFoundError,
    ServiceUnavailableError,
)
from boilerplate.errors.core import CoreError
from boilerplate.types.http_status import HttpStatus
from slowapi.errors import RateLimitExceeded


def register_errors(app: FastAPI) -> None:

    def create_exception_handler(
        status_code: int,
        default_message: str = "An unexpected error occurred",
        default_error_code: str | None = None,
    ) -> Callable[
        [Request, CoreError | Exception | RateLimitExceeded],
        Coroutine[Any, Any, Response],
    ]:

        async def exception_handler(
            request: Request, exception: CoreError | Exception | RateLimitExceeded
        ) -> Response:
            message = getattr(exception, "message", default_message)
            error_code = getattr(exception, "id", default_error_code)
            http_status_code = getattr(exception, "status_code", status_code)
            headers = getattr(exception, "headers", None)

            logging.error(
                f" {message} [cause: {getattr(exception, "cause", None)}] [error_code: {error_code}] [status_code: {http_status_code}] ",
            )

            response = JSONResponse(
                status_code=http_status_code,
                content={
                    "error_code": error_code,
                    "message": message,
                },
                headers=headers,
            )

            if isinstance(exception, RateLimitExceeded):
                response = request.app.state.limiter._inject_headers(
                    response, request.state.view_rate_limit
                )

            return response

        return exception_handler

    app.add_exception_handler(
        exc_class_or_status_code=RateLimitExceeded,
        handler=create_exception_handler(
            HttpStatus.TOO_MANY_REQUESTS,
            "Rate limit exceeded: Too many requests",
            "rate_limit_exceeded",
        ),
    )

    app.add_exception_handler(
        exc_class_or_status_code=CoreError,
        handler=create_exception_handler(status_code=HttpStatus.INTERNAL_SERVER_ERROR),
    )

    app.add_exception_handler(
        exc_class_or_status_code=NotFoundError,
        handler=create_exception_handler(status_code=HttpStatus.NOT_FOUND),
    )

    app.add_exception_handler(
        exc_class_or_status_code=AuthenticationError,
        handler=create_exception_handler(status_code=HttpStatus.FORBIDDEN),
    )

    app.add_exception_handler(
        exc_class_or_status_code=AuthorizationError,
        handler=create_exception_handler(status_code=HttpStatus.UNAUTHORIZED),
    )

    app.add_exception_handler(
        exc_class_or_status_code=BadGatewayError,
        handler=create_exception_handler(status_code=HttpStatus.BAD_GATEWAY),
    )

    app.add_exception_handler(
        exc_class_or_status_code=BadRequestError,
        handler=create_exception_handler(status_code=HttpStatus.BAD_REQUEST),
    )

    app.add_exception_handler(
        exc_class_or_status_code=ServiceUnavailableError,
        handler=create_exception_handler(status_code=HttpStatus.SERVICE_UNAVAILABLE),
    )

    app.add_exception_handler(
        exc_class_or_status_code=RepositoryError,
        handler=create_exception_handler(status_code=HttpStatus.INTERNAL_SERVER_ERROR),
    )
    app.add_exception_handler(
        exc_class_or_status_code=RepositoryNotFoundError,
        handler=create_exception_handler(status_code=HttpStatus.NOT_FOUND),
    )
    app.add_exception_handler(
        exc_class_or_status_code=DataIntegrityError,
        handler=create_exception_handler(status_code=HttpStatus.CONFLICT),
    )
    app.add_exception_handler(
        exc_class_or_status_code=ConcurrencyError,
        handler=create_exception_handler(status_code=HttpStatus.CONFLICT),
    )
    app.add_exception_handler(
        exc_class_or_status_code=ConflictError,
        handler=create_exception_handler(status_code=HttpStatus.CONFLICT),
    )
    app.add_exception_handler(
        exc_class_or_status_code=ApplicationError,
        handler=create_exception_handler(status_code=HttpStatus.INTERNAL_SERVER_ERROR),
    )
    app.add_exception_handler(
        exc_class_or_status_code=DomainError,
        handler=create_exception_handler(status_code=HttpStatus.UNPROCESSABLE_ENTITY),
    )
