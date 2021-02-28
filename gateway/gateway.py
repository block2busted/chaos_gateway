from fastapi import APIRouter
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from .httpx_requests import (
    get_user_profile_web,
    get_user_profile_mobile
)

routers = APIRouter()


@routers.get('/web/profile/')
async def profile_web(
        request: Request
):
    profile_response = await get_user_profile_web(
        request=request,
        params=request.query_params.dict
    )
    return JSONResponse(content=profile_response, status_code=status.HTTP_200_OK)


@routers.get('/mobile/profile/')
async def profile_mobile(
        request: Request
):
    profile_response = await get_user_profile_mobile(
        request=request,
        params=request.query_params.dict
    )
    return JSONResponse(content=profile_response, status_code=status.HTTP_200_OK)
