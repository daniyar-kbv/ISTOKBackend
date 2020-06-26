from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from users.models import MainUser, ClientProfile, MerchantProfile, UserActivation, ProjectPurposeType, ProjectPurpose, \
    ProjectTag, ProjectPurposeSubType, ProjectStyle, ProjectType, ProjectCategory, ProfileDocument, City, Country, \
    Specialization, MerchantPhone, CodeVerification, MerchantReview, ReviewReply, ReviewDocument, ReviewReplyDocument, \
    ClientRating
from profiles.models import FormUserAnswer, Notification, UsersPaidFeature
from nested_inline.admin import NestedStackedInline, NestedModelAdmin

import constants


# @admin.register(ProfileDocument)
# class CityTagAdmin(admin.ModelAdmin):
#     list_display = ('id', 'user', 'document')


class InlineClientProfile(admin.StackedInline):
    model = ClientProfile
    extra = 0
    readonly_fields = ['rating', ]


class InlineMerchantProfile(admin.StackedInline):
    model = MerchantProfile
    extra = 0
    filter_horizontal = ('categories', 'specializations', 'tags')
    readonly_fields = ['rating']


class InlineMerchantPhone(admin.StackedInline):
    model = MerchantPhone
    extra = 0


class InlineProfileDocument(admin.StackedInline):
    model = ProfileDocument
    extra = 0


class InlineFormUserAnswer(admin.StackedInline):
    model = FormUserAnswer
    extra = 0


class InlineNotification(admin.StackedInline):
    model = Notification
    extra = 0


class InlineUsersPaidFeature(admin.StackedInline):
    model = UsersPaidFeature
    extra = 0
    readonly_fields = ['refresh_count', ]


@admin.register(MainUser)
class MainUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'role', 'is_active', 'is_staff')
    inlines = [InlineClientProfile, InlineMerchantProfile, InlineMerchantPhone, InlineProfileDocument,
               InlineFormUserAnswer, InlineNotification, InlineUsersPaidFeature]
    list_filter = ['role', 'is_staff', 'is_active']
    search_fields = ['email', 'merchant_profile__first_name']
    readonly_fields = ['role', 'password', 'email']

    def get_changelist(self, request, **kwargs):
        from utils.admin.custom_change_list import ChangeList
        return ChangeList

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


class InlineSpecialization(admin.StackedInline):
    model = Specialization
    extra = 0


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image')
    inlines = [InlineProjectTag, InlineSpecialization]


class InlineProjectPurposeSubType(admin.StackedInline):
    model = ProjectPurposeSubType
    extra = 0


class InlineProjectPurpose(admin.StackedInline):
    model = ProjectPurpose
    extra = 0


@admin.register(ProjectPurposeType)
class ProjectPurposeTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [InlineProjectPurposeSubType, InlineProjectPurpose]


@admin.register(ProjectPurposeSubType)
class ProjectPurposeSubTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(ProjectType)
class ProjectTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(ProjectStyle)
class ProjectStyleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(ProjectPurpose)
class ProjectPurposeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(ProjectTag)
class ProjectTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class InlineCity(admin.StackedInline):
    model = City
    extra = 0


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    inlines = [InlineCity, ]


@admin.register(City)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class InlineCodeVerification(admin.StackedInline):
    model = CodeVerification


@admin.register(MerchantPhone)
class CityTagAdmin(admin.ModelAdmin):
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


@admin.register(MerchantReview)
class MerchantReviewAdmin(NestedModelAdmin):
    list_display = ('id', 'user', 'merchant')
    filter_horizontal = ('user_likes', )
    inlines = [InlineReviewDocument, InlineReviewReply]
    readonly_fields = ['user_likes', 'likes_count', 'rating']


@admin.register(ReviewReply)
class ReviewReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'review')
    filter_horizontal = ('user_likes', )
    inlines = [InlineReviewReplyDocument, ]


@admin.register(ClientRating)
class ClientRatingAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'client', 'rating']
    ordering = ['-creation_date', ]
    readonly_fields = ['rating', ]
