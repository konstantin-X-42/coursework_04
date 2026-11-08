from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings


# 1. Модель «Получатель рассылки» (Клиент)
class Client(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=255, verbose_name="Ф. И. О.")
    comment = models.TextField(blank=True, null=True, verbose_name="Комментарий")

    # ТЗ: Привязка к создателю объекта
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец"
    )

    def __str__(self):
        return f"{self.full_name} ({self.email})"

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"


# 2. Модель «Сообщение»
class Message(models.Model):
    title = models.CharField(max_length=255, verbose_name="Тема письма")
    body = models.TextField(verbose_name="Тело письма")

    # ТЗ: Привязка к создателю объекта
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец"
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


# 3. Модель «Рассылка»
class Mailing(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создана'),
        ('started', 'Запущена'),
        ('completed', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created', verbose_name="Статус")

    # Связи сущностей
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Client, verbose_name="Получатели")

    # ТЗ: Привязка к создателю объекта
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Владелец"
    )

    # Валидация на уровне сохранения (чистый Django-way)
    def clean(self):
        super().clean()
        if not self.pk and self.start_time < timezone.now():
            raise ValidationError({'start_time': 'Дата начала рассылки не может быть в прошлом.'})

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({'end_time': 'Дата окончания должна быть позже даты начала.'})

    # Динамический пересчет статуса
    def update_status(self):
        now = timezone.now()
        old_status = self.status

        if now < self.start_time:
            new_status = 'created'
        elif self.start_time <= now <= self.end_time:
            new_status = 'started'
        else:
            new_status = 'completed'

        if old_status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def __str__(self):
        return f"Рассылка {self.pk} (Статус: {self.get_status_display()})"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"

        # Права доступа для роли Менеджера по ТЗ
        permissions = [
            ('can_view_any_mailings', 'Может просматривать любые рассылки'),
            ('can_disable_mailing', 'Может отключать рассылки'),
        ]


# 4. Модель «Попытка рассылки»
class MailingLog(models.Model):
    STATUS_CHOICES = [
        ('success', 'Успешно'),
        ('failed', 'Не успешно'),
    ]

    attempt_time = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Статус")
    server_response = models.TextField(blank=True, null=True, verbose_name="Ответ почтового сервера")
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='logs', verbose_name="Рассылка")

    def __str__(self):
        return f"Попытка для рассылки {self.mailing.pk} от {self.attempt_time} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        # Исправление: добавляем автоматическую сортировку от новых логов к старым
        ordering = ['-attempt_time']
