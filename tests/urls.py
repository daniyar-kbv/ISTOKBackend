from django.urls import path
from rest_framework import routers
from tests.views import ProjectViewSet, BlogPostViewSet, MerchantReviewViewSet

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('blogs', BlogPostViewSet)
router.register('reviews', MerchantReviewViewSet)

urlpatterns += router.urls
