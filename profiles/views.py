from rest_framework import viewsets, mixins, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action
from profiles.serializers import ClientProfileGetSerializer
from users.models import MainUser
import constants


class ProfileViewSet(viewsets.GenericViewSet):
    queryset = MainUser.objects.all()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request, pk=None):
        user = request.user
        if user.role == constants.ROLE_CLIENT:
            serializer = ClientProfileGetSerializer(user)
            return Response(serializer.data)
