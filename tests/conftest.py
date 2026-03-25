from pathlib import Path
import os
import sys


ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

os.environ.setdefault("db_name", "test_db")
os.environ.setdefault("db_password", "test_password")
os.environ.setdefault("db_user", "test_user")
os.environ.setdefault("db_url", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("redis_host", "localhost")
os.environ.setdefault("redis_port", "6379")
os.environ.setdefault("redis_url", "redis://localhost:6379")
os.environ.setdefault("secret_key", "test-secret-key")
os.environ.setdefault("better_stack_api_token", "test-token")

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
