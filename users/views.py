from rest_framework.response import Response
from rest_framework import viewsets, mixins
from rest_framework import status
from rest_framework.decorators import action
from rest_framework_jwt.settings import api_settings

from django.shortcuts import redirect

from users.models import MainUser, UserActivation, CodeVerification, MerchantPhone
from users.serializers import ClientProfileCreateSerializer, MerchantProfileCreateSerializer, UserLoginSerializer, \
    CodeVerificationSerializer

from utils import encryption
from utils import response
from random import randrange

import constants
import requests
import logging

logger = logging.getLogger(__name__)

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserViewSet(viewsets.GenericViewSet,
                  mixins.CreateModelMixin):
    queryset = MainUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ClientProfileCreateSerializer

    def create(self, request, *args, **kwargs):
        user = request.data.get('user')
        role = user.get('role')
        email = user.get('email')
        phones = request.data.pop('phones')
        logger.info(f'Registration with email: {email} ({constants.ROLES[0]}) started')
        if role == constants.ROLE_CLIENT:
            serializer = ClientProfileCreateSerializer(data=request.data)
        elif role == constants.ROLE_MERCHANT:
            serializer = MerchantProfileCreateSerializer(data=request.data, context=phones)
        else:
            return Response(response.make_messages([constants.RESPONSE_INVALID_ROLE]), status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            try:
                user = MainUser.objects.get(email=email)
            except MainUser.DoesNotExist:
                return Response(response.make_messages([constants.RESPONSE_SERVER_ERROR]), status.HTTP_500_INTERNAL_SERVER_ERROR)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            data = {
                'token': token
            }
            return Response(data, status=status.HTTP_200_OK, headers=headers)
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login_regular(self, request, pk=None):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            phone = serializer.data.get('phone')
            password = serializer.data.get('password')
            if not email and not phone:
                return Response(response.make_messages([constants.RESPONSE_ENTER_EMAIL_OR_PHONE]))
            if email and phone:
                return Response(response.make_messages([constants.RESPONSE_ENTER_ONLY_EMAIL_OR_PHONE]))
            if email:
                try:
                    user = MainUser.objects.get(email=email)
                except MainUser.DoesNotExist:
                    return Response(
                        response.make_messages(
                            [[constants.EMAIL, constants.RESPONSE_USER_EMAIL_NOT_EXIST]]
                        ),
                        status=status.HTTP_400_BAD_REQUEST
                    )
            elif phone:
                try:
                    user = MainUser.objects.get(phone=phone)
                except MainUser.DoesNotExist:
                    return Response(
                        response.make_messages([constants.PHONE, constants.RESPONSE_USER_PHONE_NOT_EXIST]),
                        status=status.HTTP_400_BAD_REQUEST
                    )
            if user.check_password(password):
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                data = {
                    'token': token
                }
                return Response(data, status.HTTP_200_OK)
            return Response(
                response.make_messages([[constants.PASSWORD, constants.INCORRECT]]),
                status.HTTP_400_BAD_REQUEST
            )
        return Response(response.make_errors(serializer), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], name='send-activation-email')
    def send_activation_email(self, request, pk=None):
        email = request.data.get('email')
        role = request.data.get('role')
        if email and role:
            if UserActivation.objects.filter(email=email).count() == 0:
                activation = UserActivation.objects.create(email=email, role=role)
                activation._request = request
                activation._created = True
                activation.save()
                return Response(status.HTTP_200_OK)
            else:
                try:
                    activation = UserActivation.objects.get(email=email)
                except UserActivation.DoesNotExist:
                    return Response(response.make_messages([constants.RESPONSE_SERVER_ERROR]),
                                    status.HTTP_500_INTERNAL_SERVER_ERROR)
                if activation.user:
                    return Response(response.make_messages([constants.RESPONSE_USER_EXISTS]),
                                    status.HTTP_400_BAD_REQUEST)
                activation.delete()
                activation = UserActivation.objects.create(email=email, role=role)
                activation._request = request
                activation._created = True
                activation.save()
                return Response(status.HTTP_200_OK)
        if not email and not role:
            return Response(response.make_messages([response.missing_field('Email'), response.missing_field(role)]),
                            status.HTTP_400_BAD_REQUEST)
        if not email:
            return Response(response.make_messages([response.missing_field('Email')]), status.HTTP_400_BAD_REQUEST)
        if not role:
            return Response(response.make_messages([response.missing_field("Роль")]), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], name='verify-email')
    def verify_email(self, request, pk=None):
        email = encryption.decrypt(pk)
        try:
            activation = UserActivation.objects.get(email=email)
        except UserActivation.DoesNotExist:
            #  TODO: if no activation
            return redirect('https://docs.djangoproject.com/en/3.0/topics/http/shortcuts/')
        if activation.is_active:
            # TODO: if active
            return redirect('https://docs.djangoproject.com/en/3.0/topics/http/shortcuts/')
        # TODO: if not active
        return redirect('https://docs.djangoproject.com/en/3.0/topics/http/shortcuts/')

    @action(detail=False, methods=['post'])
    def verify_phone(self, request, pk=None):
        code = randrange(1000, 10000)
        while CodeVerification.objects.filter(code=code, phone__is_valid=True).count() > 0:
            code = randrange(1000, 10000)
        data = request.data
        data['code'] = f'{code}'
        serializer = CodeVerificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status.HTTP_200_OK)
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_code(self, request, pk=None):
        serializer = CodeVerificationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                verification = CodeVerification.objects.get(phone__phone=serializer.validated_data.get('phone').get('phone'))
                if verification.code != serializer.validated_data.get('code'):
                    return Response(constants.RESPONSE_VERIFICATION_INVALID_CODE, status.HTTP_400_BAD_REQUEST)
            except CodeVerification.DoesNotExist:
                return Response(constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST, status.HTTP_400_BAD_REQUEST)
            merchant_phone = verification.phone
            merchant_phone.is_valid = True
            merchant_phone.save()
            return Response(status.HTTP_200_OK)
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def social_start(self, request, pk=None):
        response = requests.request('get', 'https://www.facebook.com/v7.0/dialog/oauth?client_id=250967092789703&redirect_uri=http://localhost:8990/&response_type=code%20token/')
        print(response.raw)
        return Response()