from django.urls import path
from profiles.views import ProfileViewSet
from rest_framework import routers

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('', ProfileViewSet)

urlpatterns += router.urls