from celery import Celery
from settings import CELERY_BROKER_URL


app = Celery('tasks', broker=CELERY_BROKER_URL)
