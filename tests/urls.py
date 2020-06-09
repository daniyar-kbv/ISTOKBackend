from django.urls import path
from rest_framework import routers
from tests.views import ProjectViewSet

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('projects', ProjectViewSet)

urlpatterns += router.urls
