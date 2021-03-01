from celery import Celery


app = Celery('chaos')
app.config_from_object('settings')
app.conf.beat_schedule = {

}
app.autodiscover_tasks()
