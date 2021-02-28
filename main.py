from fastapi import FastAPI
from starlette.middleware import Middleware

from starlette.middleware.cors import CORSMiddleware

from middlewares import InitLocalVarsMiddleware, AuthMiddleware, AfterAuthMiddleware
from routers import routers


origins = [
    "http://localhost:3001",
    "https://localhost:3001",
    "http://192.168.101.75:3001",
    "http://134.122.73.229:3050"
]

headers = [
    'access-control-allow-credentials',
    'access-control-allow-headers,'
    'accept',
    'ccept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Access-Control-Allow-Headers',
    'Access-Control-Allow-Credentials',
    'set-cookie',
    'access-control-allow-methods',
    'access-control-allow-origin',
    'X-Request-Id'
]

middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["OPTIONS", "DELETE", "GET", "POST", "PUT"],
        allow_headers=headers,
        ),
    Middleware(InitLocalVarsMiddleware),
    Middleware(AuthMiddleware),
    Middleware(AfterAuthMiddleware)
]

app = FastAPI(middleware=middleware)
app.include_router(routers)
