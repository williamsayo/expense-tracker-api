from enum import StrEnum


class ERROR_IDS(StrEnum):
    """Enumerates supported error ids values."""
    INVALID_REQUEST_BODY = "invalid_request_body"
    MISSING_REQUEST_BODY = "missing_request_body"
    SERVICE_UNAVAILABLE = "service_unavailable"

class RepositoryErrorID(StrEnum):
    """Enumerates supported repository error id values."""

    CONCURRENCY = "repository_concurrency_error"
    CONFLICT = "repository_conflict_error"
    DATA_INTEGRITY = "repository_data_integrity_error"
    NOT_FOUND = "repository_not_found_error"
    UNEXPECTED = "repository_unexpected_error"