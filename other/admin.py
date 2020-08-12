from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from other.models import FAQ, MailingRecipient, Mailing


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'position')
    search_fields = ['question', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


@admin.register(MailingRecipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'subscription_date')
    ordering = ['-subscription_date']
    search_fields = ['email']
    list_filter = ['subscription_date', 'is_subscribed']


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'creation_date')
    search_fields = ['title', 'text', ]
    list_filter = ['creation_date']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }