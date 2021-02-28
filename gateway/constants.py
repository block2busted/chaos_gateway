from settings import RC_MODE


if RC_MODE == 'dev':
    AUTH_ACCESS_TOKEN_EXPIRE = 60*60*2  # 2 hours
else:
    AUTH_ACCESS_TOKEN_EXPIRE = 60*30  # 30 minutes
AUTH_REFRESH_TOKEN_EXPIRE = 60*60*24*60  # 60 days

NOT_AUTH_VIEWS = ('admin', 'login', 'logout')
