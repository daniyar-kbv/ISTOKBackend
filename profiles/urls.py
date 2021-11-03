from django.urls import path
from profiles.views import ProfileViewSet, IsPhoneValidView, ApplicationViewSet
from rest_framework import routers

urlpatterns = [
    path('phone_is_valid/', IsPhoneValidView.as_view()),

]

router = routers.DefaultRouter()
router.register('profile', ProfileViewSet)
router.register('applications', ApplicationViewSet)

urlpatterns += router.urls