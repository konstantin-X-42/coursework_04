from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
from .services import send_mailing_job


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Добавляем задачу: выполнять функцию send_mailing_job каждую минуту
    scheduler.add_job(
        send_mailing_job,
        trigger="interval",
        seconds=60,
        id="send_mailing_every_minute",
        max_instances=1,
        replace_existing=True,
    )

    scheduler.start()
    print("🚀 Фоновый планировщик рассылок успешно запущен!")
