import json
import time
import jwt

from fastapi import FastAPI, Request
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from gateway import _thread_locals
from gateway.constants import NOT_AUTH_VIEWS
from gateway.use_cases.chaos_logger import _logger as logger
# from gateway.utils import get_response_with_auth
from gateway.utils import get_response_with_auth_cookies, get_response_with_auth_headers

from settings import SECRET_KEY

app = FastAPI()


class InitLocalVarsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        _thread_locals.request_start_time = time.time()
        _thread_locals._request = request
        _thread_locals._request_id = request.headers.get('x-request-id', '')

        request_route = request['path']
        _thread_locals._request_route = request_route
        _thread_locals.safe_path = request_route.split('/')[-2] in NOT_AUTH_VIEWS
        _thread_locals._client_type = request_route.split('/')[1]

        return await call_next(request)


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        _thread_locals._user = {
            'user_id': '',
            'Authorization': '',
            'refresh_token': ''
        }
        client_type = _thread_locals._client_type
        if not _thread_locals.safe_path:
            if client_type == 'web':
                request = await self.check_auth_web(request=request)
            elif client_type == 'mobile':
                request = await self.check_auth_mobile(request=request)

        if isinstance(request, Exception):
            return await self.process_middleware_exception(exception=request)
        return await call_next(request)

    @staticmethod
    async def get_access_refresh_tokens(
            request: Request,
            client_type: str
    ) -> [str, str]:
        if client_type == 'web':
            access_token = request.cookies.get('Authorization', b'')
            refresh_token = request.cookies.get('refresh_token', b'')
        else:
            access_token = request.headers.get('Authorization', b'')
            refresh_token = request.headers.get('refresh_token', b'')

        if isinstance(access_token, str):
            access_token = access_token.encode('iso-8859-1')
        if isinstance(refresh_token, str):
            refresh_token = refresh_token.encode('iso-8859-1')

        return access_token, refresh_token

    async def check_auth_web(self, request: Request):
        _thread_locals._user = {
            'user_id': None,
            'Authorization': None,
            'refresh_token': None
        }
        access_token, refresh_token = await self.get_access_refresh_tokens(request, 'web')

        if access_token:
            try:
                payload = jwt.decode(access_token.decode('utf-8'), SECRET_KEY)
            except jwt.ExpiredSignatureError as e:
                e.status_code = status.HTTP_401_UNAUTHORIZED
                e.detail = 'Token expired'
                return e
            except jwt.DecodeError as e:
                e.status_code = status.HTTP_401_UNAUTHORIZED
                e.detail = 'Could not decode token'
                return e
            except jwt.InvalidTokenError as e:
                e.status_code = status.HTTP_401_UNAUTHORIZED
                e.detail = 'Invalid token'
                return e
            _thread_locals._user = {
                'user_id': payload['id'],
                'Authorization': access_token.decode('utf8'),
                'refresh_token': refresh_token.decode('utf8')

            }
        return request

    async def check_auth_mobile(self, request: Request):
        access_token, refresh_token = await self.get_access_refresh_tokens(request, 'mobile')

        if access_token:
            try:
                payload = jwt.decode(
                    access_token.decode('utf8'),
                    SECRET_KEY
                )
            except jwt.ExpiredSignatureError as e:
                e.status_code = status.HTTP_401_UNAUTHORIZED
                e.detail = 'Token expired'
                return e
            except jwt.DecodeError as e:
                e.status_code = status.HTTP_401_UNAUTHORIZED
                e.detail = 'Could not decode token'
                return e
            except jwt.InvalidTokenError as e:
                e.status_code = status.HTTP_401_UNAUTHORIZED
                e.detail = 'Invalid token'
                return e
            _thread_locals._user = {
                'user_id': payload['id'],
                'Authorization': access_token.decode('utf8'),
                'refresh_token': refresh_token.decode('utf8')

            }
        return request

    @classmethod
    async def process_middleware_exception(cls, exception):
        exception_records = {
            'request_id': _thread_locals._request_id,
            'route': _thread_locals._request_route
        }
        logger.error('', records=exception_records, exception=exception)

        response_data = {
            'status': exception.status_code,
            'payload': None,
            'error': {
                'code': 'code_code_code',
                'message': exception.detail
            }
        }
        response = JSONResponse(content=response_data, status_code=status.HTTP_200_OK)
        return await cls.get_response_with_auth(response)

    @classmethod
    async def get_response_with_auth(cls, response: Response) -> Response:
        if _thread_locals._client_type == 'web':
            return await get_response_with_auth_cookies(
                response=response
            )
        elif _thread_locals._client_type == 'mobile':
            return await get_response_with_auth_headers(
                response=response
            )


class AfterAuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
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

        response_logs_data = {
            'request_id': _thread_locals._request_id,
            'route': _thread_locals._request_route,
            'status_code': response.status_code,
            'response_data': 'response.data',
            'request_response_time': time.time() - _thread_locals.request_start_time
        }
        logger.info('', records=response_logs_data)
        return await self.get_response_with_auth(response)

    @classmethod
    async def get_response_with_auth(cls, response: Response) -> Response:
        if _thread_locals._client_type == 'web':
            return await get_response_with_auth_cookies(
                response=response
            )
        elif _thread_locals._client_type == 'mobile':
            return await get_response_with_auth_headers(
                response=response
            )
