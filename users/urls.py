from django.urls import path
from .views import UserLoginView, UserLogoutView, UserRegisterView, verify_email_view, UserProfileView

# Явно указываем имя пространства имен строкой, чтобы избежать ошибок импорта
app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('verify/<str:token>/', verify_email_view, name='verify_email'),
]
