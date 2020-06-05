from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from blog.models import BlogPost
from blog.serializers import BlogPostSearchSerializer, BlogPostDetailSerializer
from utils import pagination


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
