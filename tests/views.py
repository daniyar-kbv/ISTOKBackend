from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from tests.serializers import ProjectCreateSerializer, BlogPostCreateSerializer, MerchantReviewCreateSerialzier, \
    MerchantReviewReplyCreateSerializer
from main.models import Project, ProjectComment, ProjectCommentReply
from blog.models import BlogPost
from users.models import MerchantReview, ReviewReply


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
        print('data')
        serializer = MerchantReviewReplyCreateSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
