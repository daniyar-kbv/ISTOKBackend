from rest_framework import serializers
from main.models import Project, ProjectDocument, ProjectComment, ProjectCommentDocument
from blog.models import BlogPost, PostDocument
from users.models import MerchantReview, ReviewDocument, ReviewReply


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        tags = validated_data.pop('tags')

        project = Project.objects.create(**validated_data)

        for tag in tags:
            project.tags.add(tag)

        documents = self.context.get('documents')

        print(documents)

        if documents:
            for document in documents:
                ProjectDocument.objects.create(project=project, document=document)
        return project


class BlogPostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('user_likes')

        post = BlogPost.objects.create(**validated_data)

        documents = self.context.get('documents')

        if documents:
            for document in documents:
                PostDocument.objects.create(post=post, document=document)
        return post


class MerchantReviewCreateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = MerchantReview
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('user_likes')

        review = MerchantReview.objects.create(**validated_data)

        documents = self.context.get('documents')

        if documents:
            for document in documents:
                ReviewDocument.objects.create(review=review, document=document)
        return review


class MerchantReviewReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('user_likes')
        review = ReviewReply.objects.create(**validated_data)
        return review


class ProjectCommentCreateSerialzier(serializers.ModelSerializer):
    class Meta:
        model = ProjectComment
        fields = '__all__'

    def create(self, validated_data):
        validated_data.pop('user_likes')

        review = MerchantReview.objects.create(**validated_data)

        documents = self.context.get('documents')

        if documents:
            for document in documents:
                ReviewDocument.objects.create(review=review, document=document)
        return review
