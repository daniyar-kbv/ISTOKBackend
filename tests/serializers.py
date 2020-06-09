from rest_framework import serializers
from main.models import Project, ProjectDocument
from blog.models import BlogPost, PostDocument


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
        post = BlogPost.objects.create(**validated_data)

        documents = self.context.get('documents')

        if documents:
            for document in documents:
                PostDocument.objects.create(post=post, document=document)
        return post
