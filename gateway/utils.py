from starlette.responses import Response

from gateway import _thread_locals
from gateway.constants import AUTH_ACCESS_TOKEN_EXPIRE, AUTH_REFRESH_TOKEN_EXPIRE
from settings import COOKIES_DOMAIN, IS_SECURE_COOKIES


async def collect_auth_params(params: dict):
    params.update({
        'user_id': _thread_locals._user.get('user_id', None),
        'Authorization': _thread_locals._user.get('Authorization', None),
        'refresh_token': _thread_locals._user.get('refresh_token', None)
    })

    return params


async def update_auth_local_storage(
        access_token: str,
        refresh_token: str
) -> None:
    _thread_locals._user['Authorization'] = access_token
    _thread_locals._user['refresh_token'] = refresh_token


async def get_response_with_auth_cookies(
        response: Response
) -> Response:

    if (access_token := _thread_locals._user.get('Authorization')) is not None:
        response.set_cookie(
            key='Authorization',
            value=access_token,
            max_age=AUTH_ACCESS_TOKEN_EXPIRE,
            httponly=True,
            samesite='None',
            domain=COOKIES_DOMAIN,
            secure=IS_SECURE_COOKIES
        )
    if (refresh_token := _thread_locals._user.get('refresh_token')) is not None:
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            max_age=AUTH_REFRESH_TOKEN_EXPIRE,
            httponly=True,
            samesite='None',
            domain=COOKIES_DOMAIN,
            secure=IS_SECURE_COOKIES
        )
    return response


async def get_response_with_auth_headers(
        response: Response
) -> Response:
    response.headers['Authorization'] = _thread_locals._user.get('Authorization', '')
    response.headers['refresh_token'] = _thread_locals._user.get('refresh_token', '')
    return response
