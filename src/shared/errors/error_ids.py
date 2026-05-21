from enum import StrEnum


class ERROR_IDS(StrEnum):
    """Enumerates supported error ids values."""
    INVALID_REQUEST_BODY = "invalid_request_body"
    MISSING_REQUEST_BODY = "missing_request_body"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INVALID_CONTENT_TYPE = "invalid_content_type"
    INVALID_FILE_SIZE = "invalid_file_size"
    INVALID_FILENAME = "invalid_filename"
    DISALLOWED_FILE_EXTENSION = "disallowed_file_extension"

class RepositoryErrorID(StrEnum):
    """Enumerates supported repository error id values."""

    CONCURRENCY = "repository_concurrency_error"
    CONFLICT = "repository_conflict_error"
    DATA_INTEGRITY = "repository_data_integrity_error"
    NOT_FOUND = "repository_not_found_error"
    UNEXPECTED = "repository_unexpected_error"
