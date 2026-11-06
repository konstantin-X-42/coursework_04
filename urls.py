from django.contrib import admin
from django.urls import path, include  # <-- Обязательно добавьте импорт include сюда

urlpatterns = [
    path('admin/', admin.site.urls),

    # Подключаем маршруты приложения mailing
    path('', include('mailing.urls', namespace='mailing')),
]
