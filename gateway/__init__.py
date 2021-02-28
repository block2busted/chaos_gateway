import threading


_thread_locals = threading.local()


def get_current_request():
    return getattr(_thread_locals, '_request', None)


def get_current_request_id() -> str:
    return getattr(_thread_locals, '_request_id', '')