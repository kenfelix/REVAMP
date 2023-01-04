from celery import Celery
from celery.schedules import crontab

from .config.config import settings

username = settings.rabbitmq_username
password = settings.rabbitmq_password
vhost = settings.rabbitmq_vhost
app = Celery(
    "app",
    broker=f"amqp://{username}:{password}@localhost:5672/{vhost}",
    backend="rpc://",
    include=["app.engine", "app.utils.scraper", "app.utils.db", "app.utils.cleaned"],
)

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

app.conf.beat_schedule = {
    "execute-every-5-munites": {
        "task": "app.engine.scrape_links",
        "schedule": crontab(),
        "args": ("graphics",),
    }
}

if __name__ == "__main__":
    app.start()
