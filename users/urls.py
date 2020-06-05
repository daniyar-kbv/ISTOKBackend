from django.urls import path
from users.views import UserViewSet, ProjectReview, RegisterPage
from rest_framework import routers
from rest_framework_jwt.views import verify_jwt_token, refresh_jwt_token

urlpatterns = [
    path('token/refresh/', refresh_jwt_token, name='token_refresh'),
    path('token/verify/', verify_jwt_token, name='token_verify'),
    path('register_page/', RegisterPage.as_view())
]

router = routers.DefaultRouter()
router.register('', UserViewSet)
router.register('reviews', ProjectReview)

urlpatterns += router.urls