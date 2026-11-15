from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для управления пользователями без поля username"""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email является обязательным полем')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь иконку is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь иконку is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # Полностью убираем поле username
    username = None
    email = models.EmailField(unique=True, verbose_name='Email')

    # Дополнительные поля по ТЗ
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True, verbose_name='Аватар')
    phone = models.CharField(max_length=35, blank=True, null=True, verbose_name='Телефон')
    country = models.CharField(max_length=50, blank=True, null=True, verbose_name='Страна')

    # Поля для верификации почты
    is_verified = models.BooleanField(default=False, verbose_name='Верифицирован')
    verification_token = models.CharField(max_length=100, blank=True, null=True, verbose_name='Токен верификации')

    # Назначаем наш новый кастомный менеджер (исправляет текущую ошибку консоли)
    objects = CustomUserManager()

    # Поля авторизации
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        permissions = [
            ('can_block_user', 'Может блокировать пользователей'),
            ('can_view_any_mailings', 'Может просматривать любые рассылки'),
            ('can_disable_mailing', 'Может отключать рассылки'),
        ]

    def __str__(self):
        return self.email
