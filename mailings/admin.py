from django.contrib import admin
from .models import Client, Message, Mailing, MailingLog

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email')
    search_fields = ('full_name', 'email')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')

@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_time', 'end_time', 'status', 'message')
    list_filter = ('status',)

@admin.register(MailingLog)
class MailingLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'attempt_time', 'status', 'mailing')
    list_filter = ('status',)
