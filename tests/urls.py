from django.urls import path
from rest_framework import routers
from tests.views import ProjectViewSet, BlogPostViewSet, MerchantReviewViewSet, MerchantReviewReplyViewSet, \
    ProjectCommentViewSet, ProjectCommentReplyViewSet

urlpatterns = [
]

router = routers.DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('blogs', BlogPostViewSet)
router.register('reviews', MerchantReviewViewSet)
router.register('review_replies', MerchantReviewReplyViewSet)
router.register('project_comments', ProjectCommentViewSet)
router.register('comment_replies', ProjectCommentReplyViewSet)

urlpatterns += router.urls
