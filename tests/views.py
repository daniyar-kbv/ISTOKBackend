from django.shortcuts import render
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from tests.serializers import ProjectCreateSerializer, BlogPostCreateSerializer, MerchantReviewCreateSerialzier, \
    MerchantReviewReplyCreateSerializer, ProjectCommentCreateSerialzier, ProjectCommentReplyCreateSerializer
from main.models import Project, ProjectComment, ProjectCommentReply
from blog.models import BlogPost
from users.models import MerchantReview, ReviewReply
from utils import general
import requests, os, json


class ProjectViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin):
    serializer_class = ProjectCreateSerializer
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = ProjectCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get', 'post'])
    def tests(self, request, pk=None):
        credentials = general.encode_base64(
            # f'{os.environ.get("PAYMENTS_PUBLIC_ID")}:{os.environ.get("PAYMENTS_API_SECRET")}'
            f'{"pk_b826aa0af00e5286511d54e746fda"}:{"c40a0ba72b7ed318e713d71cb9153204"}'
        )
        headers = {
            'Authorization': f'Basic {credentials}',
            'Content-Type': 'application/json'
        }
        data = request.data
        data['IpAddress'] = general.get_client_ip(request)
        print(headers)
        print(data)
        response = requests.post('https://api.cloudpayments.ru/payments/cards/charge', headers=headers, json=data)
        return Response(response.json())

    @action(detail=False, methods=['get', 'post'])
    def pay_template(self, request, pk=None):
        return render(request, 'pay_template.html')



class BlogPostViewSet(viewsets.GenericViewSet,
                      mixins.CreateModelMixin):
    queryset = BlogPost.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = BlogPostCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MerchantReviewViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin):
    queryset = MerchantReview.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = MerchantReviewCreateSerialzier(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class MerchantReviewReplyViewSet(viewsets.GenericViewSet,
                                 mixins.CreateModelMixin):
    queryset = ReviewReply.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            review = MerchantReview.objects.get(id=request.data.get('review'))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            ReviewReply.objects.get(review=review)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            pass
        data = request.data
        data['user'] = review.merchant_id
        serializer = MerchantReviewReplyCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectCommentViewSet(viewsets.GenericViewSet,
                            mixins.CreateModelMixin):
    queryset = ProjectComment.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        context = {
            'documents': documents
        }
        serializer = ProjectCommentCreateSerialzier(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ProjectCommentReplyViewSet(viewsets.GenericViewSet,
                                 mixins.CreateModelMixin):
    queryset = ProjectCommentReply.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            comment = ProjectComment.objects.get(id=request.data.get('comment'))
        except:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        try:
            ProjectCommentReply.objects.get(comment=comment)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except:
            pass
        data = request.data
        data._mutable = True
        data['user'] = comment.project.user_id
        serializer = ProjectCommentReplyCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


