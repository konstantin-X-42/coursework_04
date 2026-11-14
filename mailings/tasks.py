from celery import shared_task
from django.utils import timezone
from .models import Mailing
from .services import send_mailing_batch


@shared_task
def send_mailing_task():
    """Периодическая Celery-задача для ежеминутной проверки и пакетной отправки рассылок"""
    now = timezone.now()

    # 1. Автоматически переводим в статус «Завершена» все рассылки, у которых вышло время
    Mailing.objects.filter(
        status__in=['created', 'started'],
        end_time__lt=now
    ).update(status='completed')

    # 2. Находим только активные (не отключенные) рассылки в текущем окне времени
    active_mailings = Mailing.objects.filter(
        status__in=['created', 'started'],
        start_time__lte=now,
        end_time__gte=now
    )

    # 3. Запускаем пакетную отправку: письмо на каждого получателя и запись в БД через bulk_create
    for mailing in active_mailings:
        send_mailing_batch(mailing)
