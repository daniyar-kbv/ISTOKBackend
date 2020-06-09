from django.urls import path
from rest_framework import routers
from tests.views import ProjectViewSet, BlogPostViewSet

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('blogs', BlogPostViewSet)

urlpatterns += router.urls
