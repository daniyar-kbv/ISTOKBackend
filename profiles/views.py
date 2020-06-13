from rest_framework import viewsets, mixins, status, permissions, views
from rest_framework.response import Response
from rest_framework.decorators import action
from profiles.serializers import ClientProfileGetSerializer, ClientProfileUpdateSerializer, UserChangePasswordSerializer
from users.serializers import PhoneSerializer
from users.models import MainUser, MerchantPhone
from profiles.models import FormQuestionGroup
from profiles.serializers import FormQuestionGroupSerializer
from utils import response
from utils.permissions import IsClient
import constants


class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.UpdateModelMixin):
    queryset = MainUser.objects.all()

    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request, pk=None):
        user = request.user
        if request.method == 'GET':
            if user.role == constants.ROLE_CLIENT:
                serializer = ClientProfileGetSerializer(user, context=request)
                return Response(serializer.data)
            elif user.role == constants.ROLE_MERCHANT:
                return Response()
        if request.method == 'PUT':
            if user.role == constants.ROLE_CLIENT:
                profile = user.profile
                email = request.data.get('email')
                if email:
                    user_data = {
                        'email': email
                    }
                else:
                    user_data = None
                phone = request.data.get('phone')
                context = {
                    'phone': phone,
                    'user_data': user_data
                }
                serializer = ClientProfileUpdateSerializer(profile, data=request.data, context=context)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status.HTTP_200_OK)
                return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
            elif user.role == constants.ROLE_MERCHANT:
                return Response()

    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        user = request.user
        serializer = UserChangePasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status.HTTP_200_OK)
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'post'], permission_classes=[IsClient])
    def client_form(self, request, pk=None):
        if request.method == 'GET':
            groups = FormQuestionGroup.objects.all().order_by('position')
            serializer = FormQuestionGroupSerializer(groups, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            return Response()


class IsPhoneValidView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['POST']

    def post(self, request, format=None):
        phone = request.data.get('phone')
        serializer = PhoneSerializer(data={
            'phone': phone
        })
        if serializer.is_valid():
            is_valid = False
            try:
                phone_obj = MerchantPhone.objects.get(phone=phone)
                is_valid = phone_obj.is_valid
            except:
                pass
            data = {
                'is_valid': is_valid
            }
            return Response(data)
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
