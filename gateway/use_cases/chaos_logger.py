import json

import stackprinter
from loguru import logger

# from worker.celery_worker import app as celery_app


_logger = logger


def loguru_request_json_formatter(message):
    """Serialize request logs to json in after_auth_middleware"""
    extra_records = message['extra']['records']
    simplified = {
        'level': message['level'].name,
        'request_id': extra_records.get('request_id'),
        'datetime': message['time'].strftime('%Y-%m-%d %H:%M:%S'),
        'route': extra_records.get('route'),
        'client_ip': extra_records.get('client_ip'),
        'user_id': extra_records.get('user_id'),
        'request_data': extra_records.get('request_data'),
    }
    serialized = json.dumps(simplified)
    message['extra']['serialized'] = serialized
    return '{extra[serialized]}'


def loguru_response_json_formatter(message):
    """Serialize response logs to json in after_auth_middleware"""
    extra_records = message['extra']['records']
    simplified = {
        'level': message['level'].name,
        'request_id': extra_records.get('request_id'),
        'route': extra_records.get('route'),
        'status_code': extra_records.get('status_code'),
        'request_response_time': extra_records.get('request_response_time'),
        'request_data': extra_records.get('request_data'),
    }
    serialized = json.dumps(simplified)
    message['extra']['serialized'] = serialized
    return '{extra[serialized]}'


def loguru_exception_json_formatter(record):
    extra_records = record['extra']['records']
    exception = record['extra']['exception']
    simplified = {
        'level': record['level'].name,
        'request_id': extra_records.get('request_id'),
        'route': extra_records.get('route'),
        'traceback': stackprinter.format(exception),
    }
    serialized = json.dumps(simplified)
    record['extra']['serialized'] = serialized
    return '{extra[serialized]}'


# def send_notification(logs):
#     """Send logs to rabbit"""
#     celery_app.send_task(
#         'worker.send_logs',
#         args=(
#             logs,
#         )
#     )


_logger.add(
    # send_notification,
    'logs/request_logs.json',
    level='INFO',
    format=loguru_request_json_formatter,
    filter=lambda record: record['extra']['records'].get('request_data'),
)
_logger.add(
    # send_notification,
    'logs/response_logs.json',
    level='INFO',
    filter=lambda record: record['extra']['records'].get('response_data'),
    format=loguru_response_json_formatter,
)
_logger.add(
    # send_notification,
    'logs/exception_logs.json',
    level='ERROR',
    filter=lambda record: record['extra'].get('exception'),
    format=loguru_exception_json_formatter,
)
