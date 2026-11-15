from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model

# Получаем класс кастомного пользователя
User = get_user_model()

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'phone', 'country', 'avatar')

class UserProfileForm(UserChangeForm):
    # Убираем поле редактирования пароля из личного кабинета
    password = None

    class Meta:
        model = User
        fields = ('email', 'phone', 'country', 'avatar')
