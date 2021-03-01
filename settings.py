import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'foo')
RC_MODE = os.environ.get('RC_MODE', 'dev')

REFRESH_TOKEN_SECRET_KEY = os.environ.get('REFRESH_TOKEN_SECRET_KEY', 'foo')
MAIN_SERVER_URL = os.environ.get('MAIN_SERVER_URL', 'http://127.0.0.1:8000')
COOKIES_DOMAIN = os.environ.get('COOKIES_DOMAIN', '127.0.0.1')
IS_SECURE_COOKIES = os.environ.get('IS_SECURE_COOKIES', False)

PUBSUB = {
    'RABBITMQ_USERNAME': os.getenv('RABBITMQ_USERNAME', 'guest'),
    'RABBITMQ_PASSWORD': os.getenv('RABBITMQ_PASSWORD', 'guest'),
    'RABBITMQ_HOST': os.getenv('RABBITMQ_HOST', 'localhost'),
    'RABBITMQ_PORT': int(os.getenv('RABBITMQ_PORT', 5672)),
}
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER', 'amqp://')
