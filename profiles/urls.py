from django.urls import path
from profiles.views import ProfileViewSet, IsPhoneValidView
from rest_framework import routers

urlpatterns = [
    path('phone_is_valid/', IsPhoneValidView.as_view()),
]

router = routers.DefaultRouter()
router.register('', ProfileViewSet)

urlpatterns += router.urls