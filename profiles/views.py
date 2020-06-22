from rest_framework import viewsets, mixins, status, permissions, views, exceptions
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from rest_framework_jwt.settings import api_settings
from django.db.models import Q
from profiles.serializers import ClientProfileGetSerializer, ClientProfileUpdateSerializer, UserChangePasswordSerializer, \
    FormUserAnswerCreatePostSerializer, ClientProfileMerchantSerializer, ApplicationBaseSerializer, \
    ApplicationClientConfirmedSerializer, ApplicationClientFinishedSerializer, ApplicationDeclinedSerializer, \
    ApplicationMerchantConfirmedDeclinedWaitingSerializer, ApplicationDeclineSerializer, ApplicationDetailSerializer, \
    ApplicationCreateSerializer, MerchantProfileTopSerializer, MerchantProfileGetSerializer, MerchantProfileForUpdate, \
    MerchantProfileUpdate, PaidFeatureTypeListSerializer
from users.serializers import PhoneSerializer, ClientRatingCreateSerializer, MerchantReviewCreateSerializer
from users.models import MainUser, MerchantPhone
from profiles.models import FormQuestionGroup, Application, ApplicationDocument, PaidFeatureType, Transaction, \
    UsersPaidFeature
from profiles.serializers import FormQuestionGroupSerializer
from utils import response, pagination
from utils.permissions import IsClient, IsAuthenticated, IsMerchant, HasPhone
import constants

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.UpdateModelMixin):
    queryset = MainUser.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request, pk=None):
        request.data._mutable = True
        user = request.user
        if request.method == 'GET':
            if user.role == constants.ROLE_CLIENT:
                serializer = ClientProfileGetSerializer(user, context=request)
                return Response(serializer.data)
            elif user.role == constants.ROLE_MERCHANT:
                serializer = MerchantProfileGetSerializer(user, context=request)
                return Response(serializer.data)
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
                phones = []
                if request.data.get('phones'):
                    phones = request.data.pop('phones')
                documents = []
                if request.data.get('documents'):
                    documents = request.data.pop('documents')
                delete_documents = []
                if request.data.get('delete_documents'):
                    delete_documents = request.data.pop('delete_documents')
                total_documents = request.data.get('total_documents')
                if total_documents:
                    try:
                        if int(total_documents) > 6:
                            return Response(response.make_messages([f'{constants.RESPONSE_MAX_FILES} 6']),
                                            status.HTTP_400_BAD_REQUEST)
                    except:
                        return Response(
                            response.make_messages([f'total_documents: {constants.RESPONSE_RIGHT_ONLY_DIGITS}']),
                            status.HTTP_400_BAD_REQUEST
                        )
                else:
                    return Response(response.make_messages([f'total_documents: {constants.RESPONSE_FIELD_REQUIRED}']),
                                    status.HTTP_400_BAD_REQUEST)
                context = {
                    'phones': phones,
                    'documents': documents,
                    'delete_documents': delete_documents,
                    'email': request.data.get('email')
                }
                profile = request.user.profile
                serializer = MerchantProfileUpdate(profile, data=request.data, context=context)
                if serializer.is_valid():
                    serializer.save()
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    data = {
                        'token': token
                    }
                    return Response(data)
                return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

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
            serializer = FormUserAnswerCreatePostSerializer(data=request.data, context=request)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def client(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages([f'Пользователь {pk} {constants.RESPONSE_DOES_NOT_EXIST}']),
                            status.HTTP_400_BAD_REQUEST)
        if user.role == constants.ROLE_MERCHANT:
            return Response(response.make_messages([constants.RESPONSE_USER_NOT_CLIENT]), status.HTTP_400_BAD_REQUEST)
        serializer = ClientProfileMerchantSerializer(user, context=request)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
    def top_info(self, request, pk=None):
        user = request.user
        serializer = MerchantProfileTopSerializer(user, context=request)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
    def for_update(self, request, pk=None):
        serializer = MerchantProfileForUpdate(request.user.profile, context=request)
        return Response(serializer.data)

    @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated, IsMerchant])
    def features(self, request, pk=None):
        type = request.data.get('type')
        if not type:
            return Response(response.make_messages([f'type {constants.RESPONSE_FIELD_REQUIRED}']))
        if request.method == 'GET':
            if not isinstance(type, int) or type < 1 or type > len(constants.PAID_FEATURE_TYPES):
                return Response(response.make_messages([f'Тип {constants.RESPONSE_PAID_TYPE_INVALID}']))
            features = PaidFeatureType.objects.filter(type=type)
            serializer = PaidFeatureTypeListSerializer(features, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            try:
                type = PaidFeatureType.objects.get(id=type)
            except:
                return Response(response.make_messages([f'Типа {constants.RESPONSE_DOES_NOT_EXIST}']),
                                status.HTTP_400_BAD_REQUEST)
            transaction = Transaction.objects.create(number='test')
            if type.type == constants.PAID_FEATURE_PRO:
                UsersPaidFeature.objects.create(user=request.user, type=type, transaction=transaction, is_active=True)
                return Response(status=status.HTTP_200_OK)
            else:
                return Response()


class IsPhoneValidView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post']
    parser_classes = (FormParser, MultiPartParser, JSONParser,)

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
            if phone_obj:
                if phone_obj.user:
                    if phone_obj.user != request.user:
                        return Response(response.make_messages([constants.RESPONSE_PHONE_REGISTERED]))
            data = {
                'is_valid': is_valid
            }
            return Response(data)
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)


class ApplicationViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin):
    queryset = Application.objects.all()
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        status_name = request.GET.get('status') if request.GET.get('status') else constants.APPLICATION_CREATED_STRING
        user = request.user

        if status_name not in constants.APPLICATION_STATUSES_STRING:
            return Response(response.make_messages([constants.RESPONSE_STATUS_NOT_VALID]), status.HTTP_400_BAD_REQUEST)

        if status_name == constants.APPLICATION_CREATED_STRING:
            queryset = self.get_queryset().filter(status=constants.APPLICATION_CREATED)
            serializer_class = ApplicationBaseSerializer
        elif status_name == constants.APPLICATION_CONFIRMED_STRING:
            queryset = self.get_queryset().filter(status=constants.APPLICATION_CONFIRMED)
            if user.role == constants.ROLE_CLIENT:
                serializer_class = ApplicationClientConfirmedSerializer
            elif user.role == constants.ROLE_MERCHANT:
                serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
        elif status_name == constants.APPLICATION_FINISHED_STRING:
            queryset = self.get_queryset().filter(status=constants.APPLICATION_FINISHED)
            if user.role == constants.ROLE_CLIENT:
                serializer_class = ApplicationBaseSerializer
            elif user.role == constants.ROLE_MERCHANT:
                serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
        elif status_name == constants.APPLICATION_FINISHED_CONFIRMED_STRING:
            queryset = self.get_queryset().filter(status=constants.APPLICATION_FINISHED_CONFIRMED)
            if user.role == constants.ROLE_CLIENT:
                serializer_class = ApplicationClientFinishedSerializer
            elif user.role == constants.ROLE_MERCHANT:
                serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
        elif status_name == constants.APPLICATION_DECLINED_STRING:
            queryset = self.get_queryset().filter(Q(status=constants.APPLICATION_DECLINED_CLIENT) |
                                                  Q(status=constants.APPLICATION_DECLINED_MERCHANT))
            serializer_class = ApplicationDeclinedSerializer

        paginator = pagination.CustomPagination()
        paginator.page_size = 2
        page = paginator.paginate_queryset(queryset, request=request)

        if page is not None:
            serializer = serializer_class(page, many=True, context=request)
            return paginator.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApplicationDetailSerializer(instance, context=request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def finish(self, request, pk=None):
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
        user = request.user
        if user.role == constants.ROLE_CLIENT:
            if application.client != user:
                return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
            if application.status != constants.APPLICATION_CONFIRMED:
                return Response(response.make_messages([f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Приянятые']),
                                status.HTTP_400_BAD_REQUEST)
            context = {
                'user': user
            }
            if request.data.get('documents'):
                documents = request.data.pop('documents')
                context['documents'] = documents
            serialzier = MerchantReviewCreateSerializer(data=request.data, context=context)
            if serialzier.is_valid():
                serialzier.save(merchant=application.merchant, user=user)
                application.status = constants.APPLICATION_FINISHED
                application.save()
                return Response(serialzier.data, status.HTTP_200_OK)
            return Response(response.make_errors(serialzier), status.HTTP_400_BAD_REQUEST)
        elif user.role == constants.ROLE_MERCHANT:
            if application.merchant != user:
                return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
            if application.status != constants.APPLICATION_CONFIRMED and \
                    application.status != constants.APPLICATION_FINISHED:
                return Response(
                    response.make_messages(
                        [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают подтверждения, в процессе']
                    ),
                    status.HTTP_400_BAD_REQUEST
                )
            serializer = ClientRatingCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, client=application.client)
                application.status = constants.APPLICATION_FINISHED_CONFIRMED
                application.save()
                return Response(serializer.data, status.HTTP_200_OK)
            return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def decline(self, request, pk=None):
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
        user = request.user
        if user.role == constants.ROLE_CLIENT:
            if application.client != user:
                return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
            if application.status != constants.APPLICATION_CREATED:
                return Response(response.make_messages([f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают ответа']),
                                status.HTTP_400_BAD_REQUEST)
            application.status = constants.APPLICATION_DECLINED_CLIENT
            application.save()
            return Response(status=status.HTTP_200_OK)
        elif user.role == constants.ROLE_MERCHANT:
            if application.merchant != user:
                return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
            if application.status != constants.APPLICATION_CREATED:
                return Response(
                    response.make_messages(
                        [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые']
                    ),
                    status.HTTP_400_BAD_REQUEST
                )
            serializer = ApplicationDeclineSerializer(application, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status.HTTP_200_OK)
            return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsMerchant])
    def accept(self, request, pk=None):
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
        user = request.user
        if application.merchant != user:
            return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
        if application.status != constants.APPLICATION_CREATED:
            return Response(
                response.make_messages(
                    [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые']
                ),
                status.HTTP_400_BAD_REQUEST
            )
        application.status = constants.APPLICATION_CONFIRMED
        application.save()
        return Response(status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsClient, HasPhone])
    def resend(self, request, pk=None):
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
        if application.status != constants.APPLICATION_FINISHED_CONFIRMED:
            return Response(
                response.make_messages(
                    [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Завершенные']
                ),
                status.HTTP_400_BAD_REQUEST
            )
        context = {
        }
        if request.data.get('documents'):
            documents = request.data.pop('documents')
            context['documents'] = documents
        serializer = ApplicationCreateSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save(client=application.client, merchant=application.merchant, project=application.project)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(response.make_errors(serializer), status=status.HTTP_400_BAD_REQUEST)
