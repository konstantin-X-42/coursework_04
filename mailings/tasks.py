from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Mailing, MailingLog
import smtplib


@shared_task
def send_mailing_task():
    """Периодическая Celery-задача для ежеминутной проверки и отправки рассылок"""
    now = timezone.now()

    active_mailings = Mailing.objects.filter(
        status__in=['created', 'started'],
        start_time__lte=now,
        end_time__gte=now
    )

    for mailing in active_mailings:
        if mailing.status != 'started':
            mailing.status = 'started'
            mailing.save()

        subject = mailing.message.title
        message = mailing.message.body
        recipient_list = [client.email for client in mailing.recipients.all()]

        if recipient_list:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email='test@mailing.ru',
                    recipient_list=recipient_list,
                    fail_silently=False,
                )

                MailingLog.objects.create(
                    status='success',
                    server_response='Письмо успешно отправлено через Celery+Redis',
                    mailing=mailing
                )
            except smtplib.SMTPException as e:
                MailingLog.objects.create(
                    status='failed',
                    server_response=f'Ошибка SMTP в Celery: {str(e)}',
                    mailing=mailing
                )
