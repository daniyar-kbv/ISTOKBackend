from django.contrib import admin
from django.db.models.fields import DecimalField, FloatField, IntegerField, AutoField
from django import forms
from django.utils.translation import ugettext_lazy as _


class GteNumericForm(forms.Form):
    name = None

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        super().__init__(*args, **kwargs)

        self.fields[self.name + '_from'] = forms.FloatField(label='', required=False,
            widget=forms.NumberInput(attrs={'placeholder': _('From')}))

    class Media:
        css = {
            'all': (
                'templates/admin-numeric-filter.css',
            )
        }


class GteNumericFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    template = 'gte_filter.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        if not isinstance(field, (DecimalField, IntegerField, FloatField, AutoField)):
            raise TypeError('Class {} is not supported for {}.'.format(type(self.field), self.__class__.__name__))

        self.request = request

        if self.parameter_name is None:
            self.parameter_name = self.field.name

        if self.parameter_name + '_from' in params:
            value = params.pop(self.parameter_name + '_from')
            self.used_parameters[self.parameter_name + '_from'] = value

        if self.parameter_name + '_to' in params:
            value = params.pop(self.parameter_name + '_to')
            self.used_parameters[self.parameter_name + '_to'] = value

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + '_from', None)
        if value_from is not None and value_from != '':
            filters.update({
                self.parameter_name + '__gte': self.used_parameters.get(self.parameter_name + '_from', None),
            })

        value_to = self.used_parameters.get(self.parameter_name + '_to', None)
        if value_to is not None and value_to != '':
            filters.update({
                self.parameter_name + '__lte': self.used_parameters.get(self.parameter_name + '_to', None),
            })

        return queryset.filter(**filters)

    def expected_parameters(self):
        return [
            '{}_from'.format(self.parameter_name),
            '{}_to'.format(self.parameter_name),
        ]

    def choices(self, changelist):
        return ({
            'request': self.request,
            'parameter_name': self.parameter_name,
            'form': GteNumericForm(name=self.parameter_name, data={
                self.parameter_name + '_from': self.used_parameters.get(self.parameter_name + '_from', None),
                self.parameter_name + '_to': self.used_parameters.get(self.parameter_name + '_to', None),
            }),
        }, )


class LteNumericForm(forms.Form):
    name = None

    def __init__(self, *args, **kwargs):
        self.name = kwargs.pop('name')
        super().__init__(*args, **kwargs)

        self.fields[self.name + '_to'] = forms.FloatField(label='', required=False,
            widget=forms.NumberInput(attrs={'placeholder': _('To')}))

    class Media:
        css = {
            'all': (
                'templates/admin-numeric-filter.css',
            )
        }


class LteNumericFilter(admin.FieldListFilter):
    request = None
    parameter_name = None
    template = 'filter_numeric_range.html'

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        if not isinstance(field, (DecimalField, IntegerField, FloatField, AutoField)):
            raise TypeError('Class {} is not supported for {}.'.format(type(self.field), self.__class__.__name__))

        self.request = request

        if self.parameter_name is None:
            self.parameter_name = self.field.name

        if self.parameter_name + '_from' in params:
            value = params.pop(self.parameter_name + '_from')
            self.used_parameters[self.parameter_name + '_from'] = value

        if self.parameter_name + '_to' in params:
            value = params.pop(self.parameter_name + '_to')
            self.used_parameters[self.parameter_name + '_to'] = value

    def queryset(self, request, queryset):
        filters = {}

        value_from = self.used_parameters.get(self.parameter_name + '_from', None)
        if value_from is not None and value_from != '':
            filters.update({
                self.parameter_name + '__gte': self.used_parameters.get(self.parameter_name + '_from', None),
            })

        value_to = self.used_parameters.get(self.parameter_name + '_to', None)
        if value_to is not None and value_to != '':
            filters.update({
                self.parameter_name + '__lte': self.used_parameters.get(self.parameter_name + '_to', None),
            })

        return queryset.filter(**filters)

    def expected_parameters(self):
        return [
            '{}_from'.format(self.parameter_name),
            '{}_to'.format(self.parameter_name),
        ]

    def choices(self, changelist):
        return ({
            'request': self.request,
            'parameter_name': self.parameter_name,
            'form': LteNumericForm(name=self.parameter_name, data={
                self.parameter_name + '_from': self.used_parameters.get(self.parameter_name + '_from', None),
                self.parameter_name + '_to': self.used_parameters.get(self.parameter_name + '_to', None),
            }),
        }, )