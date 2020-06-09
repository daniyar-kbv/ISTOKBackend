from rest_framework import viewsets, mixins
from tests.serializers import ProjectCreateSerializer
from main.models import Project


class ProjectViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin):
    serializer_class = ProjectCreateSerializer
    queryset = Project.objects.all()