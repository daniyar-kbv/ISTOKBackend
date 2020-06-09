from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from tests.serializers import ProjectCreateSerializer
from main.models import Project


class ProjectViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin):
    serializer_class = ProjectCreateSerializer
    queryset = Project.objects.all()

    def create(self, request, *args, **kwargs):
        documents = request.data.getlist('documents')
        print(documents)
        context = {
            'documents': documents
        }
        serializer = ProjectCreateSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
