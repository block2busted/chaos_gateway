from fastapi import APIRouter
from gateway import gateway


routers = APIRouter()

routers.include_router(gateway.routers)
