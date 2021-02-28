import json
import os
import time

from fastapi import FastAPI, Request, Response
from starlette import status

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from gateway import _thread_locals
from chaos_logger import _logger as logger
from gateway.constants import NOT_AUTH_VIEWS
from gateway.httpx_requests import request_post, request_get, request_put
from gateway.utils import get_response_with_auth_cookies, get_response_with_auth_headers

from settings import MAIN_SERVER_URL

app = FastAPI()


class InitLocalVarsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        _thread_locals.request_start_time = time.time()
        _thread_locals._request = request
        _thread_locals._request_id = request.headers.get('x-request-id', '')

        request_route = request['path']
        _thread_locals._request_route = request_route
        _thread_locals.safe_path = request_route.split('/')[-2] in NOT_AUTH_VIEWS
        _thread_locals._gateway_platform = os.environ.get('GATEWAY_PLATFORM', 'web')

        return await call_next(request)


class AfterAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        # TODO: await request_body = json.loads(await request.body())
        request_body = None
        if decoded_request_body := '':
            request_body = json.loads(decoded_request_body)

        request_logs_data = {
            'request_id': _thread_locals._request_id,
            'route': _thread_locals._request_route,
            'client_ip': request.get('client')[0],
            'user_id': _thread_locals._user.get('user_id', 'anonymous_user'),
            'request_data': request_body
        }

        logger.info('', records=request_logs_data)

        response = await call_next(request)

        # TODO: response_data = response.data()
        response_logs_data = {
            'request_id': _thread_locals._request_id,
            'route': _thread_locals._request_route,
            'status_code': response.status_code,
            'response_data': 'response_data',
            'request_response_time': time.time() - _thread_locals.request_start_time
        }
        logger.info('', records=response_logs_data)
        return await self.get_response_with_auth(response)

    @classmethod
    async def get_response_with_auth(cls, response: Response) -> Response:
        if _thread_locals._gateway_platform == 'web':
            return await get_response_with_auth_cookies(
                response=response
            )
        elif _thread_locals._gateway_platform == 'mobile':
            return await get_response_with_auth_headers(
                response=response
            )


class ProxyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        params_with_auth = await self.collect_auth_params(params=request.query_params.dict)
        request_method = request.method

        if request_method == 'GET':
            data = await request_get(
                url=f'{MAIN_SERVER_URL}{_thread_locals._request_route}',
                params=params_with_auth
            )
        elif request_method == 'POST':
            data = await request_post(
                url=f'{MAIN_SERVER_URL}{_thread_locals._request_route}',
                params=params_with_auth,
                data=json.loads(await request.body())
            )
        elif request_method == 'PUT':
            data = await request_put(
                url=f'{MAIN_SERVER_URL}{_thread_locals._request_route}',
                params=params_with_auth,
                data=json.loads(await request.body())
            )

        response = JSONResponse(content=data, status_code=status.HTTP_200_OK)
        return response

    @classmethod
    async def collect_auth_params(
            cls,
            params: dict
    ):
        params.update({
            'user_id': _thread_locals._user.get('user_id', None),
            'Authorization': _thread_locals._user.get('Authorization', None),
            'refresh_token': _thread_locals._user.get('refresh_token', None)
        })
        return params
