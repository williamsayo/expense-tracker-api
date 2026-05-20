from functools import lru_cache

from src.core.config import settings
from aioboto3 import Session


@lru_cache(maxsize=1)
def get_aioboto3_session() -> Session:
    return Session(
        aws_access_key_id=(
            settings.aws_access_key_id.get_secret_value()
            if settings.aws_access_key_id
            else None
        ),
        aws_secret_access_key=(
            settings.aws_secret_access_key.get_secret_value()
            if settings.aws_secret_access_key
            else None
        ),
        region_name=settings.aws_s3_region,
        aws_account_id=(
            settings.aws_s3_account_id.get_secret_value()
            if settings.aws_s3_account_id
            else None
        ),
    )
