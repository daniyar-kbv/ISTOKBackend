from django.contrib import admin
from main.models import Project, ProjectDocument, ProjectComment, ProjectView, ProjectCommentReply, \
    ProjectCommentDocument
from users.models import MerchantReview

import constants


class InlineProjectDocument(admin.StackedInline):
    model = ProjectDocument


@admin.register(Project)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name')
    filter_horizontal = ('tags', )
    inlines = [InlineProjectDocument, ]


@admin.register(ProjectCommentReply)
class ProjectCommentReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'text')
    filter_horizontal = ('user_likes', )


class InlineProjectCommentDocument(admin.StackedInline):
    model = ProjectCommentDocument


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'text', 'rating')
    filter_horizontal = ('user_likes', )
    inlines = [InlineProjectCommentDocument, ]


@admin.register(ProjectView)
class ProjectViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'creation_date')
