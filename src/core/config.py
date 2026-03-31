from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    db_name: str
    db_password: str
    db_user: str
    db_url: str
    redis_host: str
    redis_port: int
    redis_url: str
    secret_key: SecretStr
    app_name: str = "APP_NAME"
    environment: str = "development"
    version: str = "0.1.0"
    jwt_algorithm: str = "HS256"
    better_stack_api_token: str
    memory_cost: int = 65536
    time_cost: int = 3
    parallelism: int = 4
    hash_len: int = 32
    salt_len: int = 16
    use_local_repository: bool = False

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env", ".env.prod"), extra="ignore"
    )

    @property
    def debug(self) -> bool:
        return self.environment == "development"


settings = Settings()  # type: ignore [call-arg]
