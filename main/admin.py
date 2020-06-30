from django.contrib import admin
from django.forms import Textarea
from django.db import models
from main.models import Project, ProjectDocument, ProjectComment, ProjectView, ProjectCommentReply, \
    ProjectCommentDocument, Render360, ProjectCommentReplyDocument, ProjectComplain, CommentComplain, \
    CommentReplyComplain
from users.models import MerchantReview
from profiles.models import ProjectPaidFeature, Application, ApplicationDocument
from nested_inline.admin import NestedStackedInline, NestedModelAdmin
from admin_numeric_filter.admin import NumericFilterModelAdmin, RangeNumericFilter
from utils.admin.custom_filters import GteNumericFilter, LteNumericFilter

import constants


class InlineProjectDocument(admin.StackedInline):
    model = ProjectDocument
    extra = 0


class InlineRender360(admin.StackedInline):
    model = Render360
    extra = 0


class InlineProjectCommentReplyDocument(NestedStackedInline):
    model = ProjectCommentReplyDocument
    extra = 0


class InlineProjectCommentReply(NestedStackedInline):
    model = ProjectCommentReply
    extra = 0
    # inlines = [InlineProjectCommentReplyDocument, ]
    readonly_fields = ['user_likes', 'likes_count']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', ]


class InlineProjectCommentDocument(NestedStackedInline):
    model = ProjectCommentDocument
    extra = 0


class InlineProjectComment(NestedStackedInline):
    model = ProjectComment
    extra = 0
    inlines = [InlineProjectCommentDocument, InlineProjectCommentReply, ]
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


class InlineApplicationDocument(NestedStackedInline):
    model = ApplicationDocument
    extra = 0


class InlineApplication(NestedStackedInline):
    model = Application
    extra = 0
    readonly_fields = ['rating', 'decline_reason']
    autocomplete_fields = ['client', 'merchant', 'category']
    inlines = [InlineApplicationDocument, ]


@admin.register(Project)
class ProjectAdmin(NestedModelAdmin, NumericFilterModelAdmin):
    list_display = ('id', 'user', 'name', 'price_from', 'price_to', 'creation_date', 'rating')
    filter_horizontal = ('tags', )
    inlines = [InlineProjectDocument, InlineRender360, InlineProjectComment, InlineProjectComplaint,
               InlineProjectPaidFeature, InlineApplication]
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


@admin.register(ProjectComplain)
class ProjectComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'text', 'creation_date', )
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', 'project']


@admin.register(CommentComplain)
class CommentComplainAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'text', 'creation_date', )
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', 'comment']


@admin.register(CommentReplyComplain)
class CommentReplyComplainAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'reply', 'text', 'creation_date', )
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', 'reply']
