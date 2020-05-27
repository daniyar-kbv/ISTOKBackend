from django.urls import path
from users.views import UserViewSet
from rest_framework import routers

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('user', UserViewSet)
# router.register('review', ReviewViewSet)

urlpatterns += router.urls