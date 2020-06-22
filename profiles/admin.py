from django.contrib import admin
from profiles.models import FormQuestionGroup, FormQuestion, FormAnswer, FormUserAnswer, ApplicationDocument, \
    Application


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


@admin.register(FormUserAnswer)
class FormUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'answer')


class InlineApplicationDocument(admin.StackedInline):
    model = ApplicationDocument


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'merchant', 'status')
    inlines = [InlineApplicationDocument, ]
