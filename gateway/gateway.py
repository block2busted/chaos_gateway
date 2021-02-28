from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from .httpx_requests import (
    get_user_profile_web,
    get_user_profile_mobile,
    get_login_web,
    get_login_mobile
)

routers = APIRouter()


@routers.get('/web/profile/')
async def profile_web(
        request: Request
):
    profile_response = await get_user_profile_web(request)
    return JSONResponse(content=profile_response, status_code=status.HTTP_200_OK)


@routers.get('/mobile/profile/')
async def profile_mobile(
        request: Request
):
    profile_response = await get_user_profile_mobile(request)
    return JSONResponse(content=profile_response, status_code=status.HTTP_200_OK)


@routers.post('/web/login/')
async def login_web(
        data: dict
):
    login_response = await get_login_web(
        data=data
    )
    return JSONResponse(content=login_response, status_code=status.HTTP_200_OK)


@routers.post('/mobile/login/')
async def login_mobile(
        data: dict
):
    login_response = await get_login_mobile(
        data=data
    )
    return JSONResponse(content=login_response, status_code=status.HTTP_200_OK)
