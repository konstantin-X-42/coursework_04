from django.core.mail import send_mail
from django.utils import timezone
from .models import Mailing, MailingLog
import smtplib


def send_mailing_job():
    """Фоновая задача, которая проверяет рассылки и отправляет их клиентам"""
    now = timezone.now()

    # Находим все рассылки, которые должны выполняться в текущий момент
    active_mailings = Mailing.objects.filter(
        status__in=['created', 'started'],
        start_time__lte=now,
        end_time__gte=now
    )

    for mailing in active_mailings:
        # Автоматически переводим статус рассылки в состояние "Запущена"
        if mailing.status != 'started':
            mailing.status = 'started'
            mailing.save()

        # Формируем тему и текст сообщения
        subject = mailing.message.title
        message = mailing.message.body

        # Собираем список email-адресов получателей
        recipient_list = [client.email for client in mailing.recipients.all()]

        if recipient_list:
            try:
                # Имитируем/отправляем фоновое письмо
                send_mail(
                    subject=subject,
                    message=message,
                    from_email='test@mailing.ru',
                    recipient_list=recipient_list,
                    fail_silently=False,
                )

                # Записываем успешную попытку в базу данных PostgreSQL
                MailingLog.objects.create(
                    status='success',
                    server_response='Письмо успешно отправлено всем получателям',
                    mailing=mailing
                )

            except smtplib.SMTPException as e:
                # Записываем лог ошибки в PostgreSQL, если сервер не ответил
                MailingLog.objects.create(
                    status='failed',
                    server_response=f'Ошибка SMTP: {str(e)}',
                    mailing=mailing
                )
