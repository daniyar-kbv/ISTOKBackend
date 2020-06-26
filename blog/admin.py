from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models
from blog.models import BlogPost, BlogPostCategory, MainPageBlogPost, PostDocument


class InlinePostDocument(admin.StackedInline):
    model = PostDocument
    extra = 0


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'creation_date')
    filter_horizontal = ['user_likes']
    inlines = (InlinePostDocument,)
    ordering = ['-creation_date']
    search_fields = ['title', 'subtitle', 'text', ]
    list_filter = ['creation_date', 'category', 'is_main', 'city']
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 5, 'cols': 150})},
    }
    autocomplete_fields = ['user', 'category', 'city']


@admin.register(BlogPostCategory)
class BlogPostCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ['name', ]
    formfield_overrides = {
        models.CharField: {'widget': Textarea(attrs={'rows': 1, 'cols': 150})},
    }


@admin.register(MainPageBlogPost)
class MainPageBlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'position')
    autocomplete_fields = ['post', ]
