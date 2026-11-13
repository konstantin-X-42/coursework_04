import smtplib
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import Mailing, MailingLog


def send_mailing_batch(mailing):
    """
    Отправляет письма каждому получателю по отдельности
    и сохраняет логи попыток пакетно через bulk_create (batch).
    """
    # 1. Защита от запуска отключенной или завершенной рассылки (требование наставника)
    if mailing.status == 'completed':
        return False, "Ошибка: рассылка отключена менеджером или уже завершена."

    now = timezone.now()
    mailing.update_status()

    # 2. Текущее время должно быть строго между началом и окончанием
    if not (mailing.start_time <= now <= mailing.end_time):
        return False, "Ошибка: текущее время не входит в период проведения рассылки."

    recipients = mailing.recipients.all()
    if not recipients.exists():
        return False, "Ошибка: в рассылке не выбраны получатели."

    logs_to_create = []
    success_count = 0
    from_email = getattr(settings, 'EMAIL_HOST_USER', 'test@mailing.ru')

    # 3. Отправляем письмо каждому получателю и формируем список объектов логов
    for client in recipients:
        try:
            send_mail(
                subject=mailing.message.title,
                message=mailing.message.body,
                from_email=from_email,
                recipient_list=[client.email],
                fail_silently=False,
            )
            logs_to_create.append(
                MailingLog(
                    status='success',
                    server_response=f'Письмо успешно отправлено на {client.email}',
                    mailing=mailing
                )
            )
            success_count += 1
        except (smtplib.SMTPException, Exception) as e:
            logs_to_create.append(
                MailingLog(
                    status='failed',
                    server_response=f'Ошибка отправки на {client.email}: {str(e)}',
                    mailing=mailing
                )
            )

    # 4. Пакетное создание всех записей в базе одним SQL-запросом (batch)
    if logs_to_create:
        MailingLog.objects.bulk_create(logs_to_create)

    return True, f"Рассылка выполнена. Успешно отправлено: {success_count} из {len(recipients)}."


def send_mailing_job():
    """Фоновая задача для периодической отправки активных рассылок"""
    now = timezone.now()
    active_mailings = Mailing.objects.filter(
        status__in=['created', 'started'],
        start_time__lte=now,
        end_time__gte=now
    )
    for mailing in active_mailings:
        send_mailing_batch(mailing)


#--------до изменения-----------------


# import smtplib
# from django.conf import settings
# from django.core.mail import send_mail
# from django.utils import timezone
# from .models import Mailing, MailingLog
#
#
# def send_mailing_batch(mailing):
#     """
#     Отправляет письма каждому получателю по отдельности
#     и сохраняет логи попыток пакетно через bulk_create (batch).
#     """
#     now = timezone.now()
#     mailing.update_status()
#
#     # текущее время должно быть строго между началом и окончанием
#     if not (mailing.start_time <= now <= mailing.end_time):
#         return False, "Ошибка: текущее время не входит в период проведения рассылки."
#
#     recipients = mailing.recipients.all()
#     if not recipients.exists():
#         return False, "Ошибка: в рассылке не выбраны получатели."
#
#     logs_to_create = []
#     success_count = 0
#     from_email = getattr(settings, 'EMAIL_HOST_USER', 'test@mailing.ru')
#
#     # Отправляем письмо каждому получателю и формируем список объектов логов
#     for client in recipients:
#         try:
#             send_mail(
#                 subject=mailing.message.title,
#                 message=mailing.message.body,
#                 from_email=from_email,
#                 recipient_list=[client.email],
#                 fail_silently=False,
#             )
#             logs_to_create.append(
#                 MailingLog(
#                     status='success',
#                     server_response=f'Письмо успешно отправлено на {client.email}',
#                     mailing=mailing
#                 )
#             )
#             success_count += 1
#         except (smtplib.SMTPException, Exception) as e:
#             logs_to_create.append(
#                 MailingLog(
#                     status='failed',
#                     server_response=f'Ошибка отправки на {client.email}: {str(e)}',
#                     mailing=mailing
#                 )
#             )
#
#     # Пакетное создание всех записей в базе одним SQL-запросом (batch)
#     if logs_to_create:
#         MailingLog.objects.bulk_create(logs_to_create)
#
#     return True, f"Рассылка выполнена. Успешно отправлено: {success_count} из {len(recipients)}."
#
#
# def send_mailing_job():
#     """Фоновая задача для периодической отправки активных рассылок"""
#     now = timezone.now()
#     active_mailings = Mailing.objects.filter(
#         status__in=['created', 'started'],
#         start_time__lte=now,
#         end_time__gte=now
#     )
#     for mailing in active_mailings:
#         send_mailing_batch(mailing)
