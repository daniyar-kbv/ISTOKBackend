from django.contrib import admin
from main.models import Project, ProjectDocument, ProjectComment, ProjectView
from users.models import MerchantReview

import constants


class InlineProjectDocument(admin.StackedInline):
    model = ProjectDocument


@admin.register(Project)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name')
    filter_horizontal = ('tags', )
    inlines = [InlineProjectDocument, ]


@admin.register(MerchantReview)
class CityTagAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'merchant')
    filter_horizontal = ('user_likes', )


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'text', 'rating')
    filter_horizontal = ('user_likes', )


@admin.register(ProjectView)
class ProjectViewAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'creation_date')
