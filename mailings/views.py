from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Mailing, Client, Message, MailingLog
from django.utils import timezone


# --- КОНТРОЛЛЕРЫ ДЛЯ РАССЫЛОК ---

class MailingListView(ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'

    # ТРЕБОВАНИЕ ИЗ ТЗ: Динамический пересчет статуса при обращении
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()  # Метод, который мы заложили в models.py
        return obj


class MailingCreateView(CreateView):
    model = Mailing
    fields = ['start_time', 'end_time', 'message', 'recipients']
    success_url = reverse_lazy('mailings:mailing_list')
    template_name = 'mailings/mailing_form.html'


class MailingUpdateView(UpdateView):
    model = Mailing
    fields = ['start_time', 'end_time', 'message', 'recipients']
    success_url = reverse_lazy('mailings:mailing_list')
    template_name = 'mailings/mailing_form.html'


class MailingDeleteView(DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailings:mailing_list')
    template_name = 'mailings/mailing_confirm_delete.html'


# --- КОНТРОЛЛЕРЫ ДЛЯ КЛИЕНТОВ ---

class ClientListView(ListView):
    model = Client
    template_name = 'mailings/client_list.html'


class ClientCreateView(CreateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailings:client_list')
    template_name = 'mailings/client_form.html'


class ClientUpdateView(UpdateView):
    model = Client
    fields = ['email', 'full_name', 'comment']
    success_url = reverse_lazy('mailings:client_list')
    template_name = 'mailings/client_form.html'


class ClientDeleteView(DeleteView):
    model = Client
    success_url = reverse_lazy('mailings:client_list')
    template_name = 'mailings/client_confirm_delete.html'


# --- КОНТРОЛЛЕРЫ ДЛЯ СООБЩЕНИЙ ---

class MessageListView(ListView):
    model = Message
    template_name = 'mailings/message_list.html'


class MessageCreateView(CreateView):
    model = Message
    fields = ['title', 'body']
    success_url = reverse_lazy('mailings:message_list')
    template_name = 'mailings/message_form.html'


class MessageUpdateView(UpdateView):
    model = Message
    fields = ['title', 'body']
    success_url = reverse_lazy('mailings:message_list')
    template_name = 'mailings/message_form.html'


class MessageDeleteView(DeleteView):
    model = Message
    success_url = reverse_lazy('mailings:message_list')
    template_name = 'mailings/message_confirm_delete.html'


# --- ГЛАВНАЯ СТРАНИЦА (Пункт 6 ТЗ) ---

class MailingHomeView(TemplateView):
    template_name = 'mailings/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Общее количество рассылок
        context['total_mailings'] = Mailing.objects.count()

        # Количество активных рассылок (ТЗ: статус 'started' и время между start и end)
        context['active_mailings'] = Mailing.objects.filter(
            status='started',
            start_time__lte=now,
            end_time__gte=now
        ).count()

        # Количество уникальных получателей
        context['unique_clients'] = Client.objects.distinct().count()

        return context


# Заглушка для ручного запуска рассылки (Логику отправки напишем на следующем шаге)
def run_mailing_view(request, pk):
    mailing = get_object_or_404(Mailing, pk=pk)
    # Здесь будет вызов функции отправки писем
    return redirect(reverse('mailings:mailing_detail', kwargs={'pk': pk}))
