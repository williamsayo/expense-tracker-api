from functools import lru_cache
from pathlib import Path
import logging
from core.config import settings
import sys
from enum import IntEnum


class LogLevel(IntEnum):
    """Enumerates supported log level values."""

    INFO = 20
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    DEBUG = 10


@lru_cache
def setup_logging(log_level: int | str | LogLevel):
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    formatter = logging.Formatter(
        "[{levelname}] {asctime} {name}: {message}",
        style="{",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)

    base_path = handle_file_path("logs")
    file_path = base_path / "app.log"
    file_handler = logging.FileHandler(file_path)
    file_handler.setFormatter(formatter)

    root_logger.handlers = [stream_handler, file_handler]


def handle_file_path(file_path) -> Path:
    path = Path(file_path)
    path.mkdir(parents=True, exist_ok=True)
    return path
