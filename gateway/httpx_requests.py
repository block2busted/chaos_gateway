import json

import httpx
from starlette.requests import Request

from gateway.utils import collect_auth_params, update_auth_local_storage
from gateway import _thread_locals
from settings import MAIN_SERVER_URL


async def request_get(
        url: str,
        params: dict
):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            url,
            params=params
        )
        if r.status_code == httpx.codes.OK:
            await update_auth_local_storage(
                access_token=r.cookies.get('Authorization', ''),
                refresh_token=r.cookies.get('refresh_token', '')
            )
            return r.json()
    return None


async def request_post(
        url: str,
        data: dict,
        params: dict = None
):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            url,
            headers={'Content-Type': 'application/json'},
            params=params,
            data=json.dumps(data),
        )
        if r.status_code == httpx.codes.OK:
            await update_auth_local_storage(
                access_token=r.cookies.get('Authorization', ''),
                refresh_token=r.cookies.get('refresh_token', '')
            )
            return r.json()
    return None


async def get_user_profile_web(request: Request) -> dict:
    params = await collect_auth_params()
    user_id = _thread_locals._user["user_id"]
    return {
        'profile': await request_get(
            f'{MAIN_SERVER_URL}/api/authentication/v1/my_profile/',
            params=params
        ),
        'premises': await request_get(
            f'{MAIN_SERVER_URL}/api/premises/v1/own_premises/{user_id}/',
            params=params
        ),
        'review_about_user': await request_post(
            f'{MAIN_SERVER_URL}/api/review/v1/all_user_review_as_owner/',
            params=params,
            data={'user_id': user_id}
        ),
        'review_by_user': await request_post(
            f'{MAIN_SERVER_URL}/api/review/v1/all_user_review/',
            params=params,
            data={'user_id': user_id}
        )
    }


async def get_user_profile_mobile(request: Request) -> dict:
    params = await collect_auth_params()
    user_id = _thread_locals._user["user_id"]
    return {
        'profile': await request_get(
            f'{MAIN_SERVER_URL}/api/authentication/v1/my_profile/',
            params=params
        ),
        'premises': await request_get(
            f'{MAIN_SERVER_URL}/api/premises/v1/own_premises/{user_id}/',
            params=params
        ),
        'review_about_user': await request_post(
            f'{MAIN_SERVER_URL}/api/review/v1/all_user_review_as_owner/',
            params=params,
            data={'user_id': user_id}
        ),
        'review_by_user': await request_post(
            f'{MAIN_SERVER_URL}/api/review/v1/all_user_review/',
            params=params,
            data={'user_id': user_id}
        )
    }


async def get_login_web(
        data: dict
):
    return await request_post(
        f'{MAIN_SERVER_URL}/api/authentication/v1/login/',
        data=data
    )


async def get_login_mobile(
        data: dict
):
    return await request_post(
        f'{MAIN_SERVER_URL}/api/authentication/v1/login/',
        data=data
    )
