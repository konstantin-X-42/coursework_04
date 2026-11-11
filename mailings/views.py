from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.forms import widgets
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from .models import Mailing, Client, Message, MailingLog
from .services import send_mailing_batch


# --- КОНТРОЛЛЕРЫ ДЛЯ РАССЫЛОК ---

class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        # Менеджер или суперпользователь видят все рассылки системы
        if self.request.user.has_perm('mailings.can_view_any_mailings') or self.request.user.is_superuser:
            return queryset
        # Обычный пользователь видит только свои рассылки
        return queryset.filter(owner=self.request.user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Ограничение доступа: чужую рассылку смотреть нельзя (кроме менеджера/суперадмина)
        if (
            obj.owner != self.request.user
            and not self.request.user.has_perm('mailings.can_view_any_mailings')
            and not self.request.user.is_superuser
        ):
            raise PermissionDenied("Вы не имеете прав на просмотр этой рассылки")
        obj.update_status()
        return obj


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    fields = ['start_time', 'end_time', 'message', 'recipients']
    success_url = reverse_lazy('mailings:mailing_list')
    template_name = 'mailings/mailing_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_time'].widget = widgets.DateTimeInput(attrs={'type': 'datetime-local'})
        form.fields['end_time'].widget = widgets.DateTimeInput(attrs={'type': 'datetime-local'})
        return form

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ['start_time', 'end_time', 'message', 'recipients']
    success_url = reverse_lazy('mailings:mailing_list')
    template_name = 'mailings/mailing_form.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['start_time'].widget = widgets.DateTimeInput(attrs={'type': 'datetime-local'})
        form.fields['end_time'].widget = widgets.DateTimeInput(attrs={'type': 'datetime-local'})
        return form

    def form_valid(self, form):
        # При редактировании дат сбрасываем статус в 'created', чтобы он заново пересчитался
        form.instance.status = 'created'
        return super().form_valid(form)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Вы не можете редактировать эту рассылку")
        return obj


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailings:mailing_list')
    template_name = 'mailings/mailing_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Вы не можете удалить эту рассылку")
        return obj


# --- КОНТРОЛЛЕРЫ ДЛЯ КЛИЕНТОВ ---

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'mailings/client_list.html'

    def get_queryset(self):
        # Менеджер и суперпользователь видят всех клиентов
        if self.request.user.has_perm('mailings.can_view_any_mailings') or self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailings:client_list')
    template_name = 'mailings/client_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailings:client_list')
    template_name = 'mailings/client_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Вы не можете редактировать этого клиента")
        return obj


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    success_url = reverse_lazy('mailings:client_list')
    template_name = 'mailings/client_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Вы не можете удалить этого клиента")
        return obj


# --- КОНТРОЛЛЕРЫ ДЛЯ СООБЩЕНИЙ ---

class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailings/message_list.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return super().get_queryset()
        return super().get_queryset().filter(owner=self.request.user)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    fields = ['title', 'body']
    success_url = reverse_lazy('mailings:message_list')
    template_name = 'mailings/message_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = Message
    fields = ['title', 'body']
    success_url = reverse_lazy('mailings:message_list')
    template_name = 'mailings/message_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Вы не можете редактировать это сообщение")
        return obj


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = Message
    success_url = reverse_lazy('mailings:message_list')
    template_name = 'mailings/message_confirm_delete.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user and not self.request.user.is_superuser:
            raise PermissionDenied("Вы не можете удалить это сообщение")
        return obj


# --- ГЛАВНАЯ СТРАНИЦА (Пункт 6 ТЗ + Статистика попыток) ---

class MailingHomeView(TemplateView):
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        context['total_mailings'] = Mailing.objects.count()
        context['active_mailings'] = Mailing.objects.filter(
            start_time__lte=now,
            end_time__gte=now
        ).exclude(status='completed').count()
        context['unique_clients'] = Client.objects.distinct().count()

        # Статистика по попыткам и отправленным сообщениям
        if self.request.user.is_authenticated:
            if self.request.user.has_perm('mailings.can_view_any_mailings') or self.request.user.is_superuser:
                logs = MailingLog.objects.all()
            else:
                logs = MailingLog.objects.filter(mailing__owner=self.request.user)
        else:
            logs = MailingLog.objects.all()

        context['success_attempts'] = logs.filter(status='success').count()
        context['failed_attempts'] = logs.filter(status='failed').count()
        context['sent_messages_count'] = context['success_attempts']

        return context



# --- РУЧНОЙ ЗАПУСК РАССЫЛКИ ---

@login_required
def run_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if mailing.owner != request.user and not request.user.is_superuser:
        raise PermissionDenied("Вы не можете запускать чужую рассылку.")

    is_ok, msg_text = send_mailing_batch(mailing)
    if is_ok:
        messages.success(request, msg_text)
    else:
        messages.error(request, msg_text)

    return redirect(reverse('mailings:mailing_detail', kwargs={'pk': pk}))


# --- ОТКЛЮЧЕНИЕ РАССЫЛКИ МЕНЕДЖЕРОМ ---

@login_required
def disable_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)

    if not request.user.has_perm('mailings.can_disable_mailing') and not request.user.is_superuser:
        raise PermissionDenied("У вас нет прав на отключение рассылок.")

    mailing.status = 'completed'
    mailing.save(update_fields=['status'])
    messages.warning(request, f"Рассылка #{mailing.pk} принудительно отключена (переведена в статус «Завершена»).")

    return redirect(reverse('mailings:mailing_detail', kwargs={'pk': pk}))
