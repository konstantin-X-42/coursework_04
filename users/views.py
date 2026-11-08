import secrets
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from .forms import UserRegisterForm, UserProfileForm
from users.models import User

class UserLoginView(LoginView):
    template_name = 'users/login.html'
    success_url = reverse_lazy('mailings:home')

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('mailings:home')

class UserRegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # ТЗ: Деактивируем пользователя до подтверждения почты
        token = secrets.token_hex(16)
        user.verification_token = token
        user.save()

        # Формируем ссылку для подтверждения
        host = self.request.get_host()
        url = f"http://{host}{reverse('users:verify_email', kwargs={'token': token})}"

        # ТЗ: Отправка письма
        send_mail(
            subject='Подтверждение регистрации',
            message=f'Для подтверждения вашей регистрации перейдите по ссылке: {url}',
            from_email='test@mailing.ru',
            recipient_list=[user.email],
            fail_silently=False,
        )
        return super().form_valid(form)

# Функция активации аккаунта при переходе по ссылке
def verify_email_view(request, token):
    user = get_object_or_404(User, verification_token=token)
    user.is_active = True
    user.is_verified = True
    user.verification_token = None
    user.save()
    return render(request, 'users/verification_success.html')

class UserProfileView(UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        # Принудительно сохраняем изменения из формы в PostgreSQL
        form.save()
        return super().form_valid(form)

# class UserProfileView(UpdateView):
#     model = User
#     form_class = UserProfileForm
#     template_name = 'users/profile.html'
#     success_url = reverse_lazy('users:profile')
#
#     def get_object(self, queryset=None):
#         return self.request.user
