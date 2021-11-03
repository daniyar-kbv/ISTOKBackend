from django.contrib import admin
from payments.models import PaidFeatureType, UsersPaidFeature, ProjectPaidFeature, ProjectLinkedPaidFeatures, \
    Transaction
from admin_numeric_filter.admin import RangeNumericFilter


class InlineTransactionUsers(admin.StackedInline):
    model = Transaction
    extra = 0
    fields = ['feature_type', 'sum', 'succeeded', 'type', 'user']
    fk_name = 'user_feature'


class InlineTransactionProjectsMain(admin.StackedInline):
    model = Transaction
    fields = ['feature_type', 'sum', 'succeeded', 'type', 'user', 'project']
    extra = 0
    fk_name = 'project_feature_main'


class InlineTransactionProjectsSecondary(admin.StackedInline):
    model = Transaction
    extra = 0
    fields = ['feature_type', 'sum', 'succeeded', 'type', 'user', 'project']
    fk_name = 'project_feature_secondary'


@admin.register(PaidFeatureType)
class PaidFeatureTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'price', 'time_amount', 'time_unit', 'position')
    search_fields = ['text', ]
    ordering = ['type']
    list_filter = ['type', ('price', RangeNumericFilter)]


@admin.register(UsersPaidFeature)
class UsersPaidFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'type')
    search_fields = ['id', ]
    inlines = [InlineTransactionUsers, ]


@admin.register(ProjectPaidFeature)
class ProjectPaidFeatureAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'type')
    search_fields = ['id', ]
    inlines = [InlineTransactionProjectsMain, InlineTransactionProjectsSecondary]


@admin.register(ProjectLinkedPaidFeatures)
class ProjectLinkedPaidFeaturesAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_feature', 'first_feature', 'second_feature')


@admin.register(Transaction)
class ProjectLinkedPaidFeaturesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'feature_type', 'type', 'sum', 'succeeded', )

