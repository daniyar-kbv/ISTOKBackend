from django.shortcuts import render, redirect
from django.urls import reverse
from rest_framework.decorators import authentication_classes
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from payments.models import PaidFeatureType, UsersPaidFeature, ProjectPaidFeature
from payments.serializers import PaidFeatureTypeListSerializer, ProjectForPromotionSerialzier, PaidFeaturePostSerializer
from main.models import Project
from main.tasks import notify_project_feature, notify_user_feature, deactivate_user_feature, deactivate_project_feature
from users.models import MainUser
from utils import response, permissions, payments, auth
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import constants, requests, logging

logger = logging.getLogger(__name__)


class PaidFeaturesAPIView(APIView):
    authentication_classes = [auth.CsrfExemptSessionAuthentication, JSONWebTokenAuthentication]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), permissions.IsMerchant(), ]
        return []

    def get(self, request):
        type = request.data.get('type')
        if not type:
            return Response(response.make_messages_new([('type', constants.RESPONSE_FIELD_REQUIRED)]))
        if not isinstance(type, int) or type < 1 or type > len(constants.PAID_FEATURE_TYPES):
            return Response(response.make_messages_new([('type', constants.RESPONSE_PAID_TYPE_INVALID)]))
        features = PaidFeatureType.objects.filter(type=type)
        serializer = PaidFeatureTypeListSerializer(features, many=True)
        return Response(serializer.data)

    def post(self, request, pk=None):
        serializer = PaidFeaturePostSerializer(data=request.data, context=request.build_absolute_uri(reverse('test_auth')))
        logger.info(f'Payment for features by user ({request.user.email}): started')
        if serializer.is_valid():
            auth_response = requests.get(request.build_absolute_uri(reverse('test_auth')), headers={
                'Authorization': f'JWT {serializer.data.get("token")}'
            })
            user = MainUser.objects.get(id=auth_response.json())
            type = PaidFeatureType.objects.get(id=serializer.data.get('type'))
            target = serializer.data.get('target')
            if target == constants.PAID_FEATURE_FOR_USER:
                instance = user
            else:
                if not pk:
                    # TODO: failure url
                    logger.error(
                        f'Payment for features by user ({request.user.email}): failed. {constants.RESPONSE_NO_PK}')
                    return redirect(f'{request.build_absolute_uri(reverse("result_page"))}?message={constants.RESPONSE_NO_PK}')
                try:
                    instance = Project.objects.get(id=pk)
                except:
                    # TODO: failure url
                    logger.error(
                        f'Payment for features by user ({request.user.email}): failed. {constants.RESPONSE_NO_PK}')
                    return redirect(f'{request.build_absolute_uri(reverse("result_page"))}?message={constants.RESPONSE_NO_PK}')
            logger.info(f'Payment for features by user ({request.user.email}): succeeded')
            return payments.make_payment(type, request, instance, target)
        # TODO: failure url
        logger.error(
            f'Payment for features by user ({request.user.email}): failed. {response.get_message(serializer)}')
        return redirect(f'{request.build_absolute_uri(reverse("result_page"))}?message={response.get_message(serializer)}')


class SecureAPIView(APIView):
    authentication_classes = [auth.CsrfExemptSessionAuthentication, ]

    def post(self, request):
        return payments.confirm_3ds(request)


class AuthAPIView(APIView):
    authentication_classes = [auth.CsrfExemptSessionAuthentication, JSONWebTokenAuthentication]
    permission_classes = [IsAuthenticated, permissions.IsMerchant]

    def get(self, request):
        return Response(request.user.id)


class ResultPageAPIView(APIView):
    authentication_classes = [auth.CsrfExemptSessionAuthentication, ]

    def get(self, request):
        return render(request, 'result_page.html')
