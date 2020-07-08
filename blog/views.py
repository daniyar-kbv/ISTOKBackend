from django.shortcuts import render
from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from blog.models import BlogPost, BlogPostCategory
from blog.serializers import BlogPostSearchSerializer, BlogPostDetailSerializer, BlogPostCategorySerializer
from utils import pagination, response
import constants


class BlogViewSet(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin):
    queryset = BlogPost.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = BlogPost.objects.search(request=request)
        paginator = pagination.CustomPagination()
        paginator.page_size = 10
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = BlogPostSearchSerializer(page, many=True, context=request)
            data = {
                'total_found': queryset.count(),
            }
            return paginator.get_paginated_response(serializer.data, additional_data=data)
        serializer = BlogPostSearchSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = BlogPostDetailSerializer(instance, context=request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        try:
            post = BlogPost.objects.get(id=pk)
        except BlogPost.DoesNotExist:
            return Response(response.make_messages_new([('post', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        try:
            post.user_likes.get(id=request.user.id)
            post.user_likes.remove(request.user)
            post.save()
        except:
            post.user_likes.add(request.user)
            post.save()
        return Response(status=status.HTTP_200_OK)


class BlogPostCategoryViewSet(viewsets.GenericViewSet,
                              mixins.ListModelMixin):
    queryset = BlogPostCategory.objects.all()
    serializer_class = BlogPostCategorySerializer
    pagination_class = None
