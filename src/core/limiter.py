from slowapi import Limiter
from typing import Callable, List, Optional, Union
from slowapi.extension import StrOrCallableStr
from slowapi.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="memory://",
    strategy="moving-window",
)


def rate_limit(
    limit: StrOrCallableStr,
    key_func: Optional[Callable[..., str]] = None,
    per_method: bool = False,
    methods: Optional[List[str]] = None,
    error_message: Optional[str] = None,
    exempt_when: Optional[Callable[..., bool]] = None,
    cost: Union[int, Callable[..., int]] = 1,
    override_defaults: bool = True,
):
    """App specific rate limit decorator."""

    def decorator(func):
        return limiter.limit(
            limit,
            key_func,
            per_method,
            methods,
            error_message,
            exempt_when,
            cost,
            override_defaults,
        )(func)

    return decorator
