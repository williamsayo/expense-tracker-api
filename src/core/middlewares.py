from fastapi.middleware import trustedhost, cors
from fastapi import FastAPI


def register_middlewares(app: FastAPI):
    """Register all middlewares"""

    app.add_middleware(
        middleware_class=cors.CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    app.add_middleware(
        middleware_class=trustedhost.TrustedHostMiddleware,
        allowed_hosts=["*"] if app.debug else ["localhost", "127.0.0.1", "0.0.0.0"],
    )
