import os
from celery import Celery
from celery.schedules import crontab

# Указываем переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Считываем конфигурацию из settings.py, префикс для настроек Celery — 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически ищем файлы tasks.py внутри всех приложений (включая mailings)
app.autodiscover_tasks()

# Настройка периодических задач (Beat расписание)
app.conf.beat_schedule = {
    'send_mailings_every_minute': {
        'task': 'mailings.tasks.send_mailing_task',
        'schedule': crontab(minute='*/1'), # Выполнять каждую минуту
    },
}
