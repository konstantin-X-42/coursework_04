from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Главная админка Django
    path('admin/', admin.site.urls),

    # Маршруты вашего приложения для рассылок
    path('', include('mailings.urls', namespace='mailings')),
]
