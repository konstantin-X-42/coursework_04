from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from .views import (
    UserLoginView, UserLogoutView, UserRegisterView,
    verify_email_view, UserProfileView, UserListView, toggle_user_block_view
)

# Явно указываем имя пространства имен строкой, чтобы избежать ошибок импорта
app_name = 'users'

urlpatterns = [
    # --- Базовая авторизация и личный кабинет ---
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('verify/<str:token>/', verify_email_view, name='verify_email'),

    # --- Управление пользователями (доступно только Менеджеру и Суперадмину) ---
    # Страница со списком всех зарегистрированных пользователей
    path('list/', UserListView.as_view(), name='user_list'),
    # Кнопка переключения активности (блокировка / разблокировка пользователя)
    path('<int:pk>/toggle-block/', toggle_user_block_view, name='toggle_user_block'),

    # --- Восстановление пароля ---
    # Шаг 1: Страница ввода Email, куда нужно отправить ссылку для сброса
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            email_template_name='users/password_reset_email.html',
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset',
    ),
    # Шаг 2: Страница подтверждения «Письмо отправлено»
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    # Шаг 3: Страница ввода нового пароля (открывается по секретной ссылке из письма)
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    # Шаг 4: Финальный экран «Пароль успешно изменен»
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]


#---до изменения------


# from django.urls import path
# from .views import UserLoginView, UserLogoutView, UserRegisterView, verify_email_view, UserProfileView
#
# # Явно указываем имя пространства имен строкой, чтобы избежать ошибок импорта
# app_name = 'users'
#
# urlpatterns = [
#     path('login/', UserLoginView.as_view(), name='login'),
#     path('logout/', UserLogoutView.as_view(), name='logout'),
#     path('register/', UserRegisterView.as_view(), name='register'),
#     path('profile/', UserProfileView.as_view(), name='profile'),
#     path('verify/<str:token>/', verify_email_view, name='verify_email'),
# ]
