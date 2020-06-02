from django.urls import path
from main.views import MainPageClient, MainPageMerchant, ProjectViewSet, MainPageFavorites, MerchantsSearch, \
    ProjectsSearch, BlogSearch, CommentViewSet
from rest_framework import routers

urlpatterns = [
    path('main_page/client/', MainPageClient.as_view()),
    path('main_page/merchant/', MainPageMerchant.as_view()),
    path('main_page/favorites/', MainPageFavorites.as_view()),
    path('search/merchants/', MerchantsSearch.as_view()),
    path('search/projects/', ProjectsSearch.as_view()),
    path('search/blog/', BlogSearch.as_view()),
]

router = routers.DefaultRouter()
router.register('projects', ProjectViewSet)
router.register('comments', CommentViewSet)

urlpatterns += router.urls