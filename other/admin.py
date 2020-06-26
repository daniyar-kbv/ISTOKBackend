from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from other.models import FAQ


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'position')
    search_fields = ['question', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
