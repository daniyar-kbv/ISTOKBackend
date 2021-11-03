from django.urls import path
from blog.views import BlogViewSet, BlogPostCategoryViewSet
from rest_framework import routers

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('posts', BlogViewSet)
router.register('categories', BlogPostCategoryViewSet)

urlpatterns += router.urls