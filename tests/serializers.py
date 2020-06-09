from rest_framework import serializers
from main.models import Project, ProjectDocument


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def create(self, validated_data):
        project = Project.objects.create(**validated_data)

        documents = self.context['documents']
        if documents:
            for document in documents:
                ProjectDocument.objects.create(project=project, document=document)
        return project
