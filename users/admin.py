from django.contrib import admin
from django import forms
from django.forms import TextInput, Textarea
from django.db import models
from django.forms.models import BaseInlineFormSet
from users.models import MainUser, ClientProfile, MerchantProfile, UserActivation, ProjectPurposeType, ProjectPurpose, \
    ProjectTag, ProjectPurposeSubType, ProjectStyle, ProjectType, ProjectCategory, ProfileDocument, City, Country, \
    Specialization, MerchantPhone, CodeVerification, MerchantReview, ReviewReply, ReviewDocument, ReviewReplyDocument, \
    ClientRating
from main.models import ReviewComplain, ReviewReplyComplain
from profiles.models import FormUserAnswer, Notification, UsersPaidFeature
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from admin_numeric_filter.admin import RangeNumericFilter, NumericFilterModelAdmin

import constants


# @admin.register(ProfileDocument)
# class CityTagAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'document')


class InlineClientProfile(admin.StackedInline):
    model = ClientProfile
    extra = 1
    readonly_fields = ['rating', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


class InlineMerchantProfile(admin.StackedInline):
    model = MerchantProfile
    extra = 1
    filter_horizontal = ('categories', 'specializations', 'tags')
    readonly_fields = ['rating']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


class InlineMerchantPhone(admin.StackedInline):
    model = MerchantPhone
    extra = 0


class InlineProfileDocument(admin.StackedInline):
    model = ProfileDocument
    extra = 0


class InlineFormUserAnswer(admin.StackedInline):
    model = FormUserAnswer
    extra = 0
    autocomplete_fields = ['answer', ]


class InlineNotification(admin.StackedInline):
    model = Notification
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


class InlineUsersPaidFeature(admin.StackedInline):
    model = UsersPaidFeature
    extra = 0
    readonly_fields = ['refresh_count', ]
    autocomplete_fields = ['type', ]


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = MainUser
        fields = ['email', 'password', 'role', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions']

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if not self.instance.pk:
            user.is_active = False
        if commit:
            user.save()
        return user


@admin.register(MainUser)
class MainUserAdmin(admin.ModelAdmin):
    fields = ['email', 'password', 'role', 'is_superuser', 'is_staff', 'is_active', 'groups', 'user_permissions']
    list_display = ('id', 'email', 'role', 'is_active', 'is_staff', 'creation_date')
    inlines = [InlineClientProfile, InlineMerchantProfile, InlineMerchantPhone, InlineProfileDocument,
               InlineFormUserAnswer, InlineNotification, InlineUsersPaidFeature]
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['email', 'merchant_profile__first_name']
    readonly_fields = ['last_login', 'creation_date']
    ordering = ['-creation_date']
    form = UserCreationForm

    def get_changelist(self, request, **kwargs):
        from utils.admin.custom_change_list import ChangeList
        return ChangeList

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ['role', 'password', 'email']
        return self.readonly_fields + ['is_active']

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if obj:
                if inline.__class__ == InlineClientProfile or inline.__class__ == InlineMerchantProfile or \
                        inline.__class__ == InlineProfileDocument or inline.__class__ == InlineFormUserAnswer or \
                        InlineUsersPaidFeature:
                    if obj.role == constants.ROLE_CLIENT and (inline.__class__ == InlineClientProfile or
                                                              inline.__class__ == InlineFormUserAnswer):
                        yield inline.get_formset(request, obj), inline
                    elif obj.role == constants.ROLE_MERCHANT and (inline.__class__ == InlineMerchantProfile or
                                                                  inline.__class__ == InlineProfileDocument or
                                                                  inline.__class__ == InlineUsersPaidFeature):
                        yield inline.get_formset(request, obj), inline
                else:
                    yield inline.get_formset(request, obj), inline


@admin.register(Specialization)
class UserActivationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(UserActivation)
class UserActivationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_active', 'creation_date')


class InlineProjectTag(admin.StackedInline):
    model = ProjectTag
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


class InlineSpecialization(admin.StackedInline):
    model = Specialization
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image')
    inlines = [InlineProjectTag, InlineSpecialization]
    search_fields = ['name']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


class InlineProjectPurposeSubType(admin.StackedInline):
    model = ProjectPurposeSubType
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


class InlineProjectPurpose(admin.StackedInline):
    model = ProjectPurpose
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }
    autocomplete_fields = ['subtype', ]


@admin.register(ProjectPurposeType)
class ProjectPurposeTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [InlineProjectPurposeSubType, InlineProjectPurpose]
    search_fields = ['name', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


@admin.register(ProjectPurposeSubType)
class ProjectPurposeSubTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name', ]


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


@admin.register(ProjectStyle)
class ProjectStyleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


@admin.register(ProjectPurpose)
class ProjectPurposeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name', ]


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class InlineCity(admin.StackedInline):
    model = City
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [InlineCity, ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }
    search_fields = ['name', ]


@admin.register(City)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name', ]


class InlineCodeVerification(admin.StackedInline):
    model = CodeVerification


@admin.register(MerchantPhone)
class MerchantPhoneAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'is_valid')
    inlines = [InlineCodeVerification]


class InlineReviewDocument(admin.StackedInline):
    model = ReviewDocument
    extra = 0


class InlineReviewReplyDocument(NestedStackedInline):
    model = ReviewReplyDocument
    extra = 0


class InlineReviewReply(NestedStackedInline):
    model = ReviewReply
    extra = 0
    inlines = [InlineReviewReplyDocument, ]
    readonly_fields = ['user_likes', 'likes_count']
    autocomplete_fields = ['user', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


@admin.register(MerchantReview)
class MerchantReviewAdmin(NumericFilterModelAdmin):
    list_display = ('id', 'user', 'merchant', 'rating', 'text', 'creation_date')
    filter_horizontal = ('user_likes', )
    inlines = [InlineReviewDocument, InlineReviewReply]
    readonly_fields = ['user_likes', 'likes_count', 'rating']
    ordering = ['-creation_date', ]
    list_filter = [('rating', RangeNumericFilter), 'creation_date', ('likes_count', RangeNumericFilter)]
    autocomplete_fields = ['user', 'merchant']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    search_fields = ['text', ]


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'review')
    filter_horizontal = ('user_likes', )
    inlines = [InlineReviewReplyDocument, ]
    search_fields = ['text', ]


@admin.register(ClientRating)
class ClientRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'client', 'rating', 'creation_date']
    ordering = ['-creation_date', ]
    readonly_fields = ['rating', ]
    list_filter = [('rating', RangeNumericFilter), 'creation_date']
    autocomplete_fields = ['user', 'client']


@admin.register(ReviewComplain)
class CommentReplyComplainAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'review', 'text', 'creation_date', )
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', 'review']


@admin.register(ReviewReplyComplain)
class CommentReplyComplainAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reply', 'text', 'creation_date', )
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', 'reply']
