from django.urls import path
from blog.views import BlogViewSet
from rest_framework import routers

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('', BlogViewSet)

urlpatterns += router.urls