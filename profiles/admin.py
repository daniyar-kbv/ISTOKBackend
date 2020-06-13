from django.contrib import admin
from profiles.models import FormQuestionGroup, FormQuestion, FormAnswer


class InlineFormAnswer(admin.StackedInline):
    model = FormAnswer


class InlineFormQuestion(admin.StackedInline):
    model = FormQuestion


@admin.register(FormQuestionGroup)
class FormQuestionGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'position')
    inlines = [InlineFormQuestion, ]


@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'position')
    inlines = [InlineFormAnswer, ]
