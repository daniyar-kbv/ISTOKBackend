from rest_framework.response import Response
from rest_framework import viewsets, mixins, views
from rest_framework import status
from rest_framework.decorators import action, authentication_classes, permission_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework_jwt.settings import api_settings
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from django.shortcuts import redirect
from django.db.models import Q
from django.contrib.auth.models import AnonymousUser
from main.models import Project, ProjectUserFavorite, ProjectView, ProjectComment
from main.serializers import ProjectMainPageSerializer, ServicesMainPageSerialzier, ProjectModalSerializer, \
    ProjectSearchSerializer, ProjectDetailSerializer, CommentDetailSerializer
from blog.models import MainPageBlogPost, BlogPost
from blog.serializers import BlogPostMainPageSerializer, BlogPostSearchSerializer
from users.models import ProjectCategory, MerchantProfile, MerchantReview, MainUser
from users.serializers import MerchantMainPageSerializer, ReviewMainPageSerializer, UserSearchSerializer
from other.models import FAQ
from other.serializers import FAQSerializer
from utils import permissions, response, pagination, projects
from random import randrange

import constants
import logging, math

logger = logging.getLogger(__name__)


@authentication_classes((JSONWebTokenAuthentication, ))
class MainPageClient(views.APIView):
    def get(self, request):
        projects = Project.objects.filter(is_top=True).order_by("creation_date")[:11]
        projects_serializer = ProjectMainPageSerializer(projects, many=True, context=request)

        blogs = BlogPost.objects.filter(is_main=True)
        blogs_serializer = BlogPostMainPageSerializer(blogs, many=True, context=request)

        services = ProjectCategory.objects.all()
        services_serializer = ServicesMainPageSerialzier(services, many=True, context=request)

        merchants = MerchantProfile.objects.all().order_by('-rating')[:11]
        merchants_serializer = MerchantMainPageSerializer(merchants, many=True, context=request)

        reviews = MerchantReview.objects.filter(rating__gte=7.5).order_by('-creation_date')[:2]
        reviews_serializer = ReviewMainPageSerializer(reviews, many=True, context=request)

        faqs = FAQ.objects.all().order_by('position')
        faqs_serializer = FAQSerializer(faqs, many=True)

        data = {
            'top_projects': projects_serializer.data,
            'blog_posts': blogs_serializer.data,
            'services': services_serializer.data,
            'top_merchants': merchants_serializer.data,
            'reviews': reviews_serializer.data,
            'faqs': faqs_serializer.data
        }
        return Response(data)


@authentication_classes((JSONWebTokenAuthentication, ))
class MainPageMerchant(views.APIView):
    def get(self, request):
        blogs = BlogPost.objects.filter(is_main=True)
        blogs_serializer = BlogPostMainPageSerializer(blogs, many=True, context=request)

        merchants = MerchantProfile.objects.all().order_by('-rating')[:11]
        merchants_serializer = MerchantMainPageSerializer(merchants, many=True, context=request)

        data = {
            'blog_posts': blogs_serializer.data,
            'top_merchants': merchants_serializer.data,
        }
        return Response(data)


@permission_classes((permissions.IsAuthenticated, ))
@authentication_classes((JSONWebTokenAuthentication, ))
class MainPageFavorites(views.APIView):
    def get(self, request):
        projects = Project.objects.filter(user_favorites__user=request.user).order_by("-user_favorites__creation_date")
        projects_serializer = ProjectMainPageSerializer(projects, many=True, context=request)
        return Response(projects_serializer.data)


class ProjectViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin):
    queryset = Project.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = Project.objects.search(request=request)
        top = queryset.filter(is_top=True).distinct()[:8]
        paginator = pagination.CustomPagination()
        paginator.page_size = 28
        page = projects.paginate_projects(request=request, queryset=queryset, paginator=paginator)
        if page is not None:
            serializer = ProjectSearchSerializer(page, many=True, context=request)
            top_serializer = ProjectSearchSerializer(top, many=True, context=request)
            data = {
                'top_projects': top_serializer.data,
                'total_found': queryset.count(),
            }
            return paginator.get_paginated_response(serializer.data, additional_data=data)
        serializer = UserSearchSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        project_serializer = ProjectDetailSerializer(instance, context=request)
        comments = ProjectComment.objects.filter(project=instance)[:5]
        comment_serializer = CommentDetailSerializer(comments, many=True, context=request)
        recents_serializer = None
        if not isinstance(request.user, AnonymousUser):
            recents = []
            views = ProjectView.objects.filter(user=request.user, project=instance).order_by('-creation_date')
            for index, view in enumerate(views):
                if not recents.__contains__(view.project) and len(recents) < 4 and view.project != instance:
                    recents.append(view.project)
            recents_serializer = ProjectSearchSerializer(recents, many=True, context=request)

            ProjectView.objects.create(user=request.user, project=instance)
        data = {
            'project': project_serializer.data,
            'comments': comment_serializer.data,
            'recents': recents_serializer if recents_serializer is None else recents_serializer.data
        }
        return Response(data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        logger.info(f'Favorite of project({pk}) user({request.user.email}) started')
        try:
            project = Project.objects.get(id=pk)
        except Project.DoesNotExist:
            logger.error(f'Favorite of project({pk}) user({request.user.email}) failed: {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages([f'Проект {constants.RESPONSE_DOES_NOT_EXIST}']), status.HTTP_400_BAD_REQUEST)
        try:
            favorite = ProjectUserFavorite.objects.get(user=request.user, project=project)
            favorite.delete()
        except:
            ProjectUserFavorite.objects.create(user=request.user, project=project)
        logger.info(f'Favorite of project({pk}) user({request.user.email}) succeeded')
        return Response(status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def modal(self, request, pk=None):
        try:
            project = self.queryset.get(id=pk)
        except Project.DoesNotExist:
            return Response(response.make_messages([f'Проект {constants.RESPONSE_DOES_NOT_EXIST}']),
                            status.HTTP_400_BAD_REQUEST)
        serializer = ProjectModalSerializer(project, context=request)
        return Response(serializer.data, status.HTTP_200_OK)


class ProjectsSearch(views.APIView):
    def get(self, request):
        search = request.GET.get('search')
        if not search:
            search = ''
        queryset = Project.objects.search(search, request)
        top = queryset.filter(is_top=True).distinct()[:8]
        paginator = pagination.CustomPagination()
        paginator.page_size = 28
        page = projects.paginate_projects(request=request, queryset=queryset, paginator=paginator)
        if page is not None:
            serializer = ProjectSearchSerializer(page, many=True, context=request)
            top_serializer = ProjectSearchSerializer(top, many=True, context=request)
            data = {
                'merchants_count': MainUser.objects.merchant_search(search).count(),
                'blog_count': BlogPost.objects.search(search).count(),
                'top_projects': top_serializer.data,
                'total_found': queryset.count(),
            }
            return paginator.get_paginated_response(serializer.data, additional_data=data)
        serializer = UserSearchSerializer(queryset, many=True)
        return Response(serializer.data)


class MerchantsSearch(views.APIView):
    def get(self, request):
        search = request.GET.get('search')
        if not search:
            search = ''
        queryset = MainUser.objects.merchant_search(search, request)
        paginator = pagination.CustomPagination()
        paginator.page_size = 18
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = UserSearchSerializer(page, many=True, context=request)
            data = {
                'projects_count': Project.objects.search(search).count(),
                'blog_count': BlogPost.objects.search(search).count(),
                'total_found': queryset.count(),
            }
            return paginator.get_paginated_response(serializer.data, additional_data=data)
        serializer = UserSearchSerializer(queryset, many=True)
        return Response(serializer.data)


class BlogSearch(views.APIView):
    def get(self, request):
        search = request.GET.get('search')
        if not search:
            search = ''
        queryset = BlogPost.objects.search(search, request)
        paginator = pagination.CustomPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = BlogPostSearchSerializer(page, many=True, context=request)
            data = {
                'projects_count': Project.objects.search(search).count(),
                'merchants_count': MainUser.objects.merchant_search(search).count(),
                'total_found': queryset.count(),
            }
            return paginator.get_paginated_response(serializer.data, additional_data=data)
        serializer = UserSearchSerializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(viewsets.GenericViewSet):
    queryset = ProjectComment.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        logger.info(f'Like of project comment ({pk}) user({request.user.email}) started')
        try:
            comment = ProjectComment.objects.get(id=pk)
        except ProjectComment.DoesNotExist:
            logger.error(
                f'Like of project comment ({pk}) user({request.user.email}) failed, {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages([f'Комментарий {constants.RESPONSE_DOES_NOT_EXIST}']),
                            status.HTTP_400_BAD_REQUEST)
        try:
            comment.user_likes.get(id=request.user.id)
            comment.user_likes.remove(request.user)
            comment.likes_count = comment.likes_count - 1
            comment.save()
        except:
            comment.user_likes.add(request.user)
            comment.likes_count = comment.likes_count + 1
            comment.save()
        logger.info(f'Like of project comment ({pk}) user({request.user.email}) succeeded')
        return Response(status.HTTP_200_OK)
