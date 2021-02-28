import jwt
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import JSONResponse

from chaos_logger import _logger as logger

from gateway import _thread_locals
from gateway.utils import get_response_with_auth_cookies
from settings import SECRET_KEY


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        _thread_locals._user = {
            'user_id': '',
            'Authorization': '',
            'refresh_token': ''
        }

        request = await self.check_auth_cookies(request=request)

        if isinstance(request, Exception):
            return await self.process_middleware_exception(exception=request)
        return await call_next(request)

    @classmethod
    async def get_access_refresh_tokens(
            cls,
            request: Request
    ) -> [str, str]:
        access_token = request.cookies.get('Authorization', b'')
        refresh_token = request.cookies.get('refresh_token', b'')

        if isinstance(access_token, str):
            access_token = access_token.encode('iso-8859-1')
        if isinstance(refresh_token, str):
            refresh_token = refresh_token.encode('iso-8859-1')

        return access_token, refresh_token

    @classmethod
    async def check_auth_cookies(cls, request: Request):
        _thread_locals._user = {
            'user_id': None,
            'Authorization': None,
            'refresh_token': None
        }
        access_token, refresh_token = await cls.get_access_refresh_tokens(request)

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
        return await get_response_with_auth_cookies(
            response=response
        )
