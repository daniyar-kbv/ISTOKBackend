from django.contrib import admin
from users.models import MainUser, ClientProfile, MerchantProfile, UserActivation, ProjectPurposeType, ProjectPurpose, \
    ProjectTag, ProjectPurposeSubType, ProjectStyle, ProjectType, ProjectCategory, ProfileDocument, City, Country, \
    Specialization, MerchantPhone, CodeVerification

import constants


@admin.register(ProfileDocument)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'document')


class InlineProfileDocuments(admin.StackedInline):
    model = ProfileDocument


class InlineClientProfile(admin.StackedInline):
    model = ClientProfile


class InlineMerchantProfile(admin.StackedInline):
    model = MerchantProfile
    filter_horizontal = ('categories', 'specializations', 'tags')


@admin.register(MainUser)
class MainUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'role', 'is_active', 'is_staff')
    inlines = [InlineClientProfile, InlineMerchantProfile]

    def get_formsets_with_inlines(self, request, obj=None):
        for inline in self.get_inline_instances(request, obj):
            if obj:
                if obj.role == constants.ROLE_CLIENT and inline.__class__ == InlineClientProfile:
                    yield inline.get_formset(request, obj), inline
                elif obj.role == constants.ROLE_MERCHANT and inline.__class__ == InlineMerchantProfile:
                    yield inline.get_formset(request, obj), inline


@admin.register(Specialization)
class UserActivationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(UserActivation)
class UserActivationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'is_active', 'creation_date')


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'image')


@admin.register(ProjectPurposeType)
class ProjectPurposeTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


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


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(City)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class InlineCodeVerification(admin.StackedInline):
    model = CodeVerification


@admin.register(MerchantPhone)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'phone', 'is_valid')
    inlines = [InlineCodeVerification]

