from fastapi import FastAPI, APIRouter

def register_routers(app: FastAPI, routers: list[APIRouter], version: str = "v1"):
    for router in routers:
        app.include_router(router, prefix=f"/api/{version}")