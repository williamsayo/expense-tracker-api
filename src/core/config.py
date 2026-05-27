from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

for env_file in sorted(BASE_DIR.glob(".env*")):
    load_dotenv(env_file, override=True)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    # Database settings
    db_name: str
    db_password: str
    db_user: str
    db_url: str
    # Redis settings
    redis_host: str
    redis_port: int
    redis_url: str
    # Application settings
    secret_key: SecretStr
    app_name: str = "APP_NAME"
    environment: str = "development"
    version: str = "0.1.0"
    # JWT settings
    jwt_algorithm: str = "HS256"
    # Logging settings
    better_stack_api_token: str
    # Argon2 settings
    memory_cost: int = 65536
    time_cost: int = 3
    parallelism: int = 4
    hash_len: int = 32
    salt_len: int = 16
    # Repository settings
    use_local_repository: bool = False
    # AWS S3 settings
    aws_access_key_id: SecretStr | None = None
    aws_secret_access_key: SecretStr | None = None
    aws_s3_bucket_name: str
    aws_s3_region: str = "eu-north-1"
    aws_s3_account_id: SecretStr | None = None
    aws_s3_bucket_url: str | None = None
    media_url: str
    # CloudFront settings
    aws_distribution_id: str
    cloudfront_private_key: SecretStr
    cloudfront_key_pair_id: str
    # API keys
    openai_api_key: SecretStr
    google_api_key: SecretStr
    # DynamoDB settings
    dynamodb_dashboard_table_name: str = "dashboard_table"
    default_avatar: str = "avatars/default.png"
    # Token settings
    access_token_expiry: int = 3600  # in seconds
    refresh_token_expiry: int = 604800  # in seconds (7 days)

    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env", ".env.prod"), extra="ignore"
    )

    @property
    def debug(self) -> bool:
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore [call-arg]


settings = get_settings()
