from django.contrib import admin
from blog.models import BlogPost, BlogPostCategory, MainPageBlogPost, PostDocument


class InlinePostDocument(admin.StackedInline):
    model = PostDocument


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user')
    filter_horizontal = ['user_likes']
    inlines = (InlinePostDocument,)


@admin.register(BlogPostCategory)
class BlogPostCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(MainPageBlogPost)
class MainPageBlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'post')
