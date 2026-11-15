from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_managers_group(sender, **kwargs):
    """
    Автоматически создает группу «Менеджеры» и назначает ей
    все необходимые права после выполнения миграций (python manage.py migrate).
    """
    from django.contrib.auth.models import Group, Permission

    # Получаем или создаем группу «Менеджеры»
    group, _ = Group.objects.get_or_create(name='Менеджеры')

    # Собираем все одноименные права менеджера из моделей User и Mailing
    codenames = [
        'can_block_user',
        'can_view_any_mailings',
        'can_disable_mailing',
    ]
    permissions = Permission.objects.filter(codename__in=codenames)

    # Привязываем найденные права к группе
    group.permissions.set(permissions)


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'Пользователи'

    def ready(self):
        # Подключаем сигнал post_migrate для автоматического создания группы при миграциях
        post_migrate.connect(create_managers_group, sender=self)
