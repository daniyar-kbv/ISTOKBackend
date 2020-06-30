from django.urls import path
from main.views import MainPageClient, MainPageMerchant, ProjectViewSet, MainPageFavorites, MerchantsSearch, \
    ProjectsSearch, BlogSearch, CommentViewSet, CityViewSet, ProjectCategoryViewSet, SpecializationViewSet, \
    ProjectTagViewSet, CountryViewSet, ProjectTypeViewSet, ProjectPurposeTypeViewSet, ProjectStyleViewSet
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
router.register('cities', CityViewSet)
router.register('categories', ProjectCategoryViewSet)
router.register('specializations', SpecializationViewSet)
router.register('project_tags', ProjectTagViewSet)
router.register('countries', CountryViewSet)
router.register('types', ProjectTypeViewSet)
router.register('purpose_types', ProjectPurposeTypeViewSet)
router.register('styles', ProjectStyleViewSet)

urlpatterns += router.urls
