from django.contrib import admin
from django.forms import Textarea
from django.db import models
from main.models import Project, ProjectDocument, ProjectComment, ProjectView, ProjectCommentReply, \
    ProjectCommentDocument, Render360, ProjectCommentReplyDocument, ProjectComplain, CommentComplain, \
    CommentReplyComplain
from users.models import MerchantReview
from profiles.models import Application, ApplicationDocument
from payments.models import ProjectPaidFeature, Transaction
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from admin_numeric_filter.admin import NumericFilterModelAdmin, RangeNumericFilter
from utils.admin.custom_filters import GteNumericFilter, LteNumericFilter

import constants


class InlineProjectDocument(NestedStackedInline):
    model = ProjectDocument
    extra = 0


class InlineRender360(NestedStackedInline):
    model = Render360
    extra = 0


class InlineProjectCommentReplyDocument(NestedStackedInline):
    model = ProjectCommentReplyDocument
    extra = 0


class InlineCommentReplyComplain(NestedStackedInline):
    model = CommentReplyComplain
    extra = 0
    autocomplete_fields = ['user']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


class InlineProjectCommentReply(NestedStackedInline):
    model = ProjectCommentReply
    extra = 0
    inlines = [InlineProjectCommentReplyDocument, InlineCommentReplyComplain]
    readonly_fields = ['user_likes', 'likes_count']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', ]


class InlineCommentComplain(NestedStackedInline):
    model = CommentComplain
    extra = 0
    autocomplete_fields = ['user']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }


class InlineProjectCommentDocument(NestedStackedInline):
    model = ProjectCommentDocument
    extra = 0


class InlineProjectComment(NestedStackedInline):
    model = ProjectComment
    extra = 0
    inlines = [InlineProjectCommentDocument, InlineCommentComplain, InlineProjectCommentReply, ]
    readonly_fields = ['rating', 'likes_count', 'user_likes']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', ]


class InlineProjectComplaint(NestedStackedInline):
    model = ProjectComplain
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', ]


class InlineProjectPaidFeature(NestedStackedInline):
    model = ProjectPaidFeature
    extra = 0
    readonly_fields = ['refresh_count', ]
    autocomplete_fields = ['type', ]


class InlineTransaction(NestedStackedInline):
    model = Transaction
    fields = ['feature_type', 'type', 'user_feature', 'project_feature_main', 'project_feature_secondary',
              'creation_date', 'succeeded', 'sum']
    extra = 0
    autocomplete_fields = ['user', 'user_feature', 'project_feature_main', 'project_feature_secondary']
    readonly_fields = ['creation_date', 'succeeded', 'sum']


class InlineApplicationDocument(NestedStackedInline):
    model = ApplicationDocument
    extra = 0


class InlineApplication(NestedStackedInline):
    model = Application
    extra = 0
    readonly_fields = ['rating', 'decline_reason', 'creation_date']
    autocomplete_fields = ['client', 'merchant', 'category']
    inlines = [InlineApplicationDocument, ]


@admin.register(Project)
class ProjectAdmin(NestedModelAdmin, NumericFilterModelAdmin):
    list_display = ('id', 'user', 'name', 'price_from', 'price_to', 'creation_date', 'rating')
    filter_horizontal = ('tags', )
    inlines = [InlineProjectDocument, InlineRender360, InlineProjectComment,
               InlineProjectPaidFeature, InlineTransaction, InlineApplication, InlineProjectComplaint]
    list_filter = ['category', 'purpose', 'type', 'style', 'tags', ('price_from', GteNumericFilter),
                   ('price_to', LteNumericFilter), ('area', RangeNumericFilter), 'is_top', 'is_detailed',
                   'creation_date', ('rating', RangeNumericFilter)]
    readonly_fields = ['rating', 'to_profile_count']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', 'category', 'purpose', 'type', 'style']
    search_fields = ['name', 'description']


@admin.register(ProjectCommentReply)
class ProjectCommentReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'text')
    filter_horizontal = ('user_likes', )
    search_fields = ['text', ]


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'text', 'rating')
    filter_horizontal = ('user_likes', )
    inlines = [InlineProjectCommentDocument, ]
    search_fields = ['text', ]


@admin.register(ProjectView)
class ProjectViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'creation_date')


class ComplainAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'text', 'is_active', 'creation_date', )
    list_filter = ['is_active', 'creation_date']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', ]
    search_fields = ['text', ]


@admin.register(ProjectComplain)
class ProjectComplaintAdmin(ComplainAdmin):
    list_display = ComplainAdmin.list_display[:2] + ('project', ) + ComplainAdmin.list_display[2:]
    autocomplete_fields = ComplainAdmin.autocomplete_fields + ['project', ]


@admin.register(CommentComplain)
class CommentComplainAdmin(ComplainAdmin):
    list_display = ComplainAdmin.list_display[:2] + ('comment', ) + ComplainAdmin.list_display[2:]
    autocomplete_fields = ComplainAdmin.autocomplete_fields + ['comment', ]


@admin.register(CommentReplyComplain)
class CommentReplyComplainAdmin(ComplainAdmin):
    list_display = ComplainAdmin.list_display[:2] + ('reply', ) + ComplainAdmin.list_display[2:]
    autocomplete_fields = ComplainAdmin.autocomplete_fields + ['reply', ]
