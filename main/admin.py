from django.contrib import admin
from main.models import Project, ProjectDocument, ProjectComment, ProjectView, ProjectCommentReply, \
    ProjectCommentDocument, Render360, ProjectCommentReplyDocument, ProjectComplaint
from users.models import MerchantReview
from profiles.models import ProjectPaidFeature
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
    inlines = [InlineProjectCommentReplyDocument, ]


class InlineProjectCommentDocument(NestedStackedInline):
    model = ProjectCommentDocument
    extra = 0


class InlineProjectComment(NestedStackedInline):
    model = ProjectComment
    extra = 0
    inlines = [InlineProjectCommentDocument, InlineProjectCommentReply, ]
    readonly_fields = ['rating', 'likes_count', 'user_likes']


class InlineProjectComplaint(NestedStackedInline):
    model = ProjectComplaint
    extra = 0


class InlineProjectPaidFeature(NestedStackedInline):
    model = ProjectPaidFeature
    extra = 0
    readonly_fields = ['refresh_count', ]


@admin.register(Project)
class CityTagAdmin(NestedModelAdmin, NumericFilterModelAdmin):
    list_display = ('id', 'user', 'name', 'price_from', 'price_to', 'creation_date', 'rating')
    filter_horizontal = ('tags', )
    inlines = [InlineProjectDocument, InlineRender360, InlineProjectComment, InlineProjectComplaint,
               InlineProjectPaidFeature]
    list_filter = ['category', 'purpose', 'type', 'style', 'tags', ('price_from', GteNumericFilter),
                   ('price_to', LteNumericFilter), ('area', RangeNumericFilter), 'is_top', 'is_detailed',
                   'creation_date', ('rating', RangeNumericFilter)]
    readonly_fields = ['rating', 'to_profile_count']


@admin.register(ProjectCommentReply)
class ProjectCommentReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'text')
    filter_horizontal = ('user_likes', )


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'text', 'rating')
    filter_horizontal = ('user_likes', )
    inlines = [InlineProjectCommentDocument, ]


@admin.register(ProjectView)
class ProjectViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'creation_date')


@admin.register(ProjectComplaint)
class ProjectComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'text', 'creation_date', )
