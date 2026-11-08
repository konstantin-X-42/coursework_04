from django.apps import AppConfig

class MailingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mailings'
    verbose_name = 'Управление рассылками'

    # def ready(self):
    #     # Импортируем и запускаем планировщик напрямую при готовности приложения
    #     from .scheduler import start_scheduler
    #     start_scheduler()


    def ready(self):
        # Оставляем метод пустым, так как теперь задачи планирует Celery Beat
        pass
