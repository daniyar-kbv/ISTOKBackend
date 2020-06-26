from django.contrib import admin
from django.forms import Textarea
from django.db import models
from profiles.models import FormQuestionGroup, FormQuestion, FormAnswer, FormUserAnswer, ApplicationDocument, \
    Application, PaidFeatureType, UsersPaidFeature, ProjectPaidFeature, Notification
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from admin_numeric_filter.admin import NumericFilterModelAdmin, RangeNumericFilter


class InlineFormAnswer(NestedStackedInline):
    model = FormAnswer
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


class InlineFormQuestion(NestedStackedInline):
    model = FormQuestion
    extra = 0
    inlines = [InlineFormAnswer, ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


@admin.register(FormQuestionGroup)
class FormQuestionGroupAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'position')
    inlines = [InlineFormQuestion, ]
    list_filter = ['position', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


@admin.register(FormQuestion)
class FormQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'position')
    inlines = [InlineFormAnswer, ]


@admin.register(FormUserAnswer)
class FormUserAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'answer')
    search_fields = ['answer', ]


@admin.register(FormAnswer)
class FormAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'answer', 'position', 'question')
    search_fields = ['answer', ]


class InlineApplicationDocument(admin.StackedInline):
    model = ApplicationDocument
    extra = 0


@admin.register(Application)
class ApplicationAdmin(NumericFilterModelAdmin):
    list_display = ('id', 'client', 'merchant', 'status', 'creation_date')
    inlines = [InlineApplicationDocument, ]
    ordering = ['-creation_date', ]
    search_fields = ['comment', 'decline_reason']
    list_filter = ['category', 'creation_date', 'status', ('rating', RangeNumericFilter)]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['client', 'merchant', 'category', 'project']


@admin.register(PaidFeatureType)
class PaidFeatureTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'price', 'time_amount', 'time_unit', 'position')
    search_fields = ['text', ]
    ordering = ['type']
    list_filter = ['type', ('price', RangeNumericFilter)]


@admin.register(UsersPaidFeature)
class UsersPaidFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type')


@admin.register(ProjectPaidFeature)
class ProjectPaidFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'type')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'creation_date')
