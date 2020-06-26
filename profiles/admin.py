from django.contrib import admin
from profiles.models import FormQuestionGroup, FormQuestion, FormAnswer, FormUserAnswer, ApplicationDocument, \
    Application, PaidFeatureType, UsersPaidFeature, ProjectPaidFeature, Notification
from nested_inline.admin import NestedStackedInline, NestedModelAdmin


class InlineFormAnswer(NestedStackedInline):
    model = FormAnswer
    extra = 0


class InlineFormQuestion(NestedStackedInline):
    model = FormQuestion
    extra = 0
    inlines = [InlineFormAnswer, ]


@admin.register(FormQuestionGroup)
class FormQuestionGroupAdmin(NestedModelAdmin):
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
    extra = 0


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'merchant', 'status')
    inlines = [InlineApplicationDocument, ]


@admin.register(PaidFeatureType)
class PaidFeatureTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'price')


@admin.register(UsersPaidFeature)
class UsersPaidFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type')


@admin.register(ProjectPaidFeature)
class ProjectPaidFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'type')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'creation_date')
