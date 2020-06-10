from rest_framework.response import Response
from rest_framework import viewsets, mixins, views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework_jwt.settings import api_settings
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser

from django.shortcuts import redirect
from django.db.models import Q

from users.models import MainUser, UserActivation, CodeVerification, MerchantReview, ProjectTag, ProjectCategory, City, \
    Specialization, Country, MerchantPhone
from users.serializers import ClientProfileCreateSerializer, MerchantProfileCreateSerializer, UserLoginSerializer, \
    CodeVerificationSerializer, UserSearchSerializer, UserTopDetailSerializer, MerchantReviewDetailList, \
    MerchantDetailSerializer, ProjectTagShortSerializer, SpecializationSerializer
from main.models import Project
from main.serializers import ProjectDetailListSerializer, ProjectCategoryShortSerializer, CitySerializer, \
    CountrySerializer
from utils import encryption, response, oauth, permissions, pagination, general
from random import randrange

import constants
import logging

logger = logging.getLogger(__name__)

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class UserViewSet(viewsets.GenericViewSet,
                  mixins.CreateModelMixin,
                  mixins.ListModelMixin):
    queryset = MainUser.objects.all()
    parser_classes = (FormParser, MultiPartParser, JSONParser,)
    http_method_names = ['get', 'post']

    def get_serializer_class(self):
        if self.action == 'create':
            return ClientProfileCreateSerializer

    def list(self, request, *args, **kwargs):
        queryset = MainUser.objects.merchant_search(request=request)
        paginator = pagination.CustomPagination()
        paginator.page_size = 18
        page = paginator.paginate_queryset(queryset, request=request)
        if page is not None:
            context = {
                'request': request
            }
            serializer = UserSearchSerializer(page, many=True, context=context)
            additional_data = {
                'total_found': queryset.count()
            }
            return paginator.get_paginated_response(serializer.data, additional_data=additional_data)
        serializer = UserSearchSerializer(queryset, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        print(request.data)
        user = {
            'email': request.data.get('email'),
            'role': int(request.data.get('role')),
            'password': request.data.get('password')
        }
        role = user.get('role')
        email = user.get('email')
        logger.info(f'Registration with email: {email} ({constants.ROLES[0]}) started')
        phones = request.data.getlist('phones')
        documents = request.data.getlist('documents')
        context = {
            'phones': phones,
            'user': user,
            'documents': documents,
            'avatar': request.data.get('avatar'),
            'rating': request.data.get('rating')
        }
        if role == constants.ROLE_CLIENT:
            serializer = ClientProfileCreateSerializer(data=request.data, context=context)
        elif role == constants.ROLE_MERCHANT:
            serializer = MerchantProfileCreateSerializer(data=request.data, context=context)
        else:
            logger.error(
                f'Registration with email: {email} ({constants.ROLES[0]}) failed: {constants.RESPONSE_INVALID_ROLE}')
            return Response(response.make_messages([constants.RESPONSE_INVALID_ROLE]), status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            try:
                user = MainUser.objects.get(email=email)
            except MainUser.DoesNotExist:
                logger.error(
                 f'Registration with email: {email} ({constants.ROLES[0]})  failed: {constants.RESPONSE_SERVER_ERROR}')
                return Response(response.make_messages([constants.RESPONSE_SERVER_ERROR]),
                                status.HTTP_500_INTERNAL_SERVER_ERROR)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            data = {
                'token': token
            }
            logger.info(
                f'Registration with email: {email} ({constants.ROLES[0]}) succeeded')
            return Response(data, status=status.HTTP_200_OK, headers=headers)
        logger.error(
            f'Registration with email: {email} ({constants.ROLES[0]}) failed: {response.make_errors(serializer)}')
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login_regular(self, request, pk=None):
        logger.info(f'Regular login ({request.data.get("email")}): started')
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get('email')
            phone = serializer.data.get('phone')
            password = serializer.data.get('password')
            if not email and not phone:
                logger.error(
                    f'Regular login ({request.data.get("email")}): failed {constants.RESPONSE_ENTER_EMAIL_OR_PHONE}')
                return Response(response.make_messages([constants.RESPONSE_ENTER_EMAIL_OR_PHONE]))
            if email and phone:
                logger.error(
                  f'Regular login ({request.data.get("email")}): failed {constants.RESPONSE_ENTER_ONLY_EMAIL_OR_PHONE}')
                return Response(response.make_messages([constants.RESPONSE_ENTER_ONLY_EMAIL_OR_PHONE]))
            if email:
                try:
                    user = MainUser.objects.get(email=email)
                except MainUser.DoesNotExist:
                    logger.error(
                        f'Regular login ({request.data.get("email")}): failed {constants.RESPONSE_USER_EMAIL_NOT_EXIST}')
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
                    logger.error(
                        f'Regular login ({request.data.get("email")}): failed {constants.RESPONSE_USER_PHONE_NOT_EXIST}')
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
                logger.info(
                    f'Regular login ({request.data.get("email")}): succeeded')
                return Response(data, status.HTTP_200_OK)
            logger.error(
                f'Regular login ({request.data.get("email")}): failed {constants.PASSWORD} {constants.INCORRECT}')
            return Response(
                response.make_messages([[constants.PASSWORD, constants.INCORRECT]]),
                status.HTTP_400_BAD_REQUEST
            )
        logger.error(
            f'Regular login ({request.data.get("email")}): failed {response.make_errors(serializer)}')
        return Response(response.make_errors(serializer), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], name='send-activation-email')
    def send_activation_email(self, request, pk=None):
        email = request.data.get('email')
        role = request.data.get('role')
        name = request.data.get('name')
        logger.info(f'Activation email sending ({email}): started')
        if email and role:
            if UserActivation.objects.filter(email=email).count() == 0:
                activation = UserActivation.objects.create(email=email, role=role, name=name)
                activation._request = request
                activation._created = True
                activation.save()
                logger.info(f'Activation email sending ({email}): succeeded')
                return Response(status.HTTP_200_OK)
            else:
                try:
                    activation = UserActivation.objects.get(email=email)
                except UserActivation.DoesNotExist:
                    logger.error(f'Activation email sending ({email}): failed {constants.RESPONSE_SERVER_ERROR}')
                    return Response(response.make_messages([constants.RESPONSE_SERVER_ERROR]),
                                    status.HTTP_500_INTERNAL_SERVER_ERROR)
                if activation.user:
                    logger.error(f'Activation email sending ({email}): failed {constants.RESPONSE_USER_EXISTS}')
                    return Response(response.make_messages([constants.RESPONSE_USER_EXISTS]),
                                    status.HTTP_400_BAD_REQUEST)
                activation.delete()
                activation = UserActivation.objects.create(email=email, role=role)
                activation._request = request
                activation._created = True
                activation.save()
                logger.info(f'Activation email sending ({email}): succeeded')
                return Response(status.HTTP_200_OK)
        if not email and not role:
            logger.error(f'Activation email sending ({response.make_messages([response.missing_field("Email"), response.missing_field(role)])}')
            return Response(response.make_messages([response.missing_field('Email'), response.missing_field(role)]),
                            status.HTTP_400_BAD_REQUEST)
        if not email:
            logger.error(f'Activation email sending ({email}): failed {response.missing_field("Email")}')
            return Response(response.make_messages([response.missing_field('Email')]), status.HTTP_400_BAD_REQUEST)
        if not role:
            logger.error(f'Activation email sending ({email}): failed {response.missing_field("Роль")}')
            return Response(response.make_messages([response.missing_field("Роль")]), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], name='verify-email')
    def verify_email(self, request, pk=None):
        email = encryption.decrypt(pk)
        logger.info(f'Email verification ({email}): started')
        try:
            activation = UserActivation.objects.get(email=email)
        except UserActivation.DoesNotExist:
            #  TODO: if no activation
            logger.error(f'Email verification ({email}): failed')
            return redirect('https://docs.djangoproject.com/en/3.0/topics/http/shortcuts/')
        if activation.is_active:
            # TODO: if active
            logger.error(f'Email verification ({email}): failed')
            return redirect('https://docs.djangoproject.com/en/3.0/topics/http/shortcuts/')
        # TODO: if not active
        logger.error(f'Email verification ({email}): failed')
        return redirect(f'http://192.168.0.107:3000/registration-specials?email={email}')

    @action(detail=False, methods=['post'])
    def verify_phone(self, request, pk=None):
        logger.info(f'Code verification ({request.data.get("phone").get("phone")}): started')
        code = randrange(1000, 10000)
        while CodeVerification.objects.filter(code=code, phone__is_valid=True).count() > 0:
            code = randrange(1000, 10000)
        data = request.data
        data['code'] = f'{code}'
        serializer = CodeVerificationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'Code verification ({request.data.get("phone").get("phone")}): succeeded')
            return Response(serializer.validated_data, status.HTTP_200_OK)
        logger.error(
            f'Code verification ({request.data.get("phone").get("phone")}): failed {response.make_errors(serializer)}')
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_code(self, request, pk=None):
        serializer = CodeVerificationSerializer(data=request.data)
        logger.info(f'Send code ({request.data.get("phone").get("phone")}): started')
        if serializer.is_valid():
            try:
                verification = CodeVerification.objects.get(phone__phone=serializer.validated_data.get('phone').get('phone'))
                if verification.code != serializer.validated_data.get('code'):
                    logger.error(f'Send code ({request.data.get("phone").get("phone")}): failed {constants.RESPONSE_VERIFICATION_INVALID_CODE}')
                    return Response(constants.RESPONSE_VERIFICATION_INVALID_CODE, status.HTTP_400_BAD_REQUEST)
            except CodeVerification.DoesNotExist:
                logger.error(
                    f'Send code ({request.data.get("phone").get("phone")}): failed {constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST}')
                return Response(constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST, status.HTTP_400_BAD_REQUEST)
            merchant_phone = verification.phone
            merchant_phone.is_valid = True
            merchant_phone.save()
            logger.error(
                f'Send code ({request.data.get("phone").get("phone")}): succeeded')
            return Response(status.HTTP_200_OK)
        logger.error(
            f'Send code ({request.data.get("phone").get("phone")}): failed {response.make_errors(serializer)}')
        return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def social_login(self, request, pk=None):
        social_type = request.data.get('social_type')
        email = request.data.get('email', '')
        phone = request.data.get('phone', '')
        role = request.data.get('role')
        if not role:
            return Response(response.make_messages(['role: Укажите роль']))
        logger.info(f'Social login ({email}, {social_type}): started')
        info, error = oauth.get_social_info(request.data, social_type)
        if not info:
            logger.error(f'Social login ({email}, {social_type}): failed {constants.RESPONSE_SERVER_ERROR}')
            return Response(constants.RESPONSE_SERVER_ERROR, status.HTTP_500_INTERNAL_SERVER_ERROR)
        if not info.get('email', '') and email:
            info['email'] = email
        if not info.get('phone', '') and phone:
            info['phone'] = phone
        if not info:
            logger.error(f'Social login ({email}, {social_type}): failed {constants.RESPONSE_SERVER_ERROR}')
            return Response(status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            if MainUser.objects.filter(email=info['email']).count() > 0:
                user = MainUser.objects.get(email=info['email'])
            else:
                phone = MerchantPhone.objects.get(phone=info['phone'])
                user = phone.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            if user.role == constants.ROLE_CLIENT:
                name = user.client_profile.first_name
            else:
                name = user.merchant_profile.first_name
            data = {
                'register': False,
                'name': name,
                'token': token
            }
            logger.info(f'Social login ({email}, {social_type}): succeeded')
            return Response(data, status.HTTP_200_OK)
        except:
            if role == constants.ROLE_CLIENT and info['email'] and info['first_name'] and info['birthday']:
                user = {
                    'email': info['email'],
                    'role': int(request.data.get('role'))
                }
                role = user.get('role')
                email = user.get('email')
                context = {
                    'user': user
                }
                info['date_of_birth'] = info['birthday']
                serializer = ClientProfileCreateSerializer(data=info, context=context)
                if serializer.is_valid():
                    profile = serializer.save()
                    user = profile.user
                    payload = jwt_payload_handler(user)
                    token = jwt_encode_handler(payload)
                    data = {
                        'register': False,
                        'token': token
                    }
                    return Response(data)
                return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
            info['register'] = True
            logger.info(f'Social login ({email}, {social_type}): succeeded')
        return Response(info, status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def top_details(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages([f'Пользователь {constants.RESPONSE_DOES_NOT_EXIST}']))
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages([constants.RESPONSE_USER_NOT_MERCHANT]))
        context = {
            'request': request
        }
        serializer = UserTopDetailSerializer(user, context=context)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages([f'Пользователь {constants.RESPONSE_DOES_NOT_EXIST}']))
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages([constants.RESPONSE_USER_NOT_MERCHANT]))
        projects = Project.objects.filter(user=user)
        paginator = pagination.CustomPagination()
        paginator.page_size = 8
        page = paginator.paginate_queryset(projects, request)
        if page is not None:
            serializer = ProjectDetailListSerializer(projects, many=True, context=request)
            return paginator.get_paginated_response(serializer.data)
        serializer = ProjectDetailListSerializer(projects, many=True, context=request)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages([f'Пользователь {constants.RESPONSE_DOES_NOT_EXIST}']),
                            status.HTTP_400_BAD_REQUEST)
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages([constants.RESPONSE_USER_NOT_MERCHANT]))
        reviews = MerchantReview.objects.filter(merchant=user)
        if request.data.get('order_by'):
            order_by = request.data.get('order_by')
        else:
            order_by = '-creation_date'
        reviews = reviews.order_by(order_by)
        paginator = pagination.CustomPagination()
        paginator.page_size = 8
        page = paginator.paginate_queryset(reviews, request)
        if page is not None:
            serializer = MerchantReviewDetailList(reviews, many=True, context=request)
            data = {
                'total_found': reviews.count()
            }
            return paginator.get_paginated_response(serializer.data, additional_data=data)
        serializer = MerchantReviewDetailList(reviews, many=True, context=request)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def details(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages([f'Пользователь {constants.RESPONSE_DOES_NOT_EXIST}']))
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages([constants.RESPONSE_USER_NOT_MERCHANT]))
        serializer = MerchantDetailSerializer(user)
        return Response(serializer.data)


class ProjectReview(viewsets.GenericViewSet):
    queryset = MerchantReview.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        logger.info(f'Like of merchant review ({pk}) user({request.user.email}) started')
        try:
            review = MerchantReview.objects.get(id=pk)
        except MerchantReview.DoesNotExist:
            logger.error(f'Like of merchant review ({pk}) user({request.user.email}) failed, {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages([f'Отзыв {constants.RESPONSE_DOES_NOT_EXIST}']), status.HTTP_400_BAD_REQUEST)
        try:
            review.user_likes.get(id=request.user.id)
            review.user_likes.remove(request.user)
            review.likes_count = review.likes_count - 1
            review.save()
        except:
            review.user_likes.add(request.user)
            review.likes_count = review.likes_count + 1
            review.save()
        logger.info(f'Like of merchant review ({pk}) user({request.user.email}) succeeded')
        return Response(status.HTTP_200_OK)


class RegisterPage(views.APIView):
    def get(self, request):
        tags = ProjectTag.objects.all()
        tags_serializer = ProjectTagShortSerializer(tags, many=True)
        countries = Country.objects.all()
        countries_serializer = CountrySerializer(countries, many=True)
        categories = ProjectCategory.objects.all()
        categories_serializer = ProjectCategoryShortSerializer(categories, many=True)
        specializations = Specialization.objects.all()
        specializations_serializer = SpecializationSerializer(specializations, many=True)
        data = {
            'categories': categories_serializer.data,
            'locations': countries_serializer.data,
            'specializations': specializations_serializer.data,
            'tags': tags_serializer.data
        }
        return Response(data)