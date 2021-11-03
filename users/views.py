from rest_framework.response import Response
from rest_framework import viewsets, mixins, views
from rest_framework import status
from rest_framework.decorators import action
from rest_framework_jwt.settings import api_settings
from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
from django.shortcuts import redirect
from users.models import MainUser, UserActivation, CodeVerification, MerchantReview, ProjectTag, ProjectCategory, City, \
    Specialization, Country, MerchantPhone, ReviewReply
from users.serializers import ClientProfileCreateSerializer, MerchantProfileCreateSerializer, UserLoginSerializer, \
    CodeVerificationSerializer, UserSearchSerializer, UserTopDetailSerializer, MerchantReviewDetailList, \
    MerchantDetailSerializer, ProjectTagShortSerializer, SpecializationSerializer
from main.models import Project, ReviewComplain, ReviewReplyComplain
from main.serializers import ProjectDetailListSerializer, ProjectCategoryShortSerializer, CitySerializer, \
    CountrySerializer, ReviewComplainSerializer, ReviewReplyComplainSerializer
from utils import encryption, response, oauth, permissions, pagination, general
from random import randrange
from datetime import datetime
from django.utils import timezone
import constants, logging

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
        user = {}
        if request.data.get('email'):
            user['email'] = request.data.get('email')
        if request.data.get('role'):
            try:
                role_int = int(request.data.get('role'))
            except:
                return Response(response.make_messages_new([('role', constants.RESPONSE_DATA_TYPES_DIGITS)]),
                                status.HTTP_400_BAD_REQUEST)
            user['role'] = role_int
        if request.data.get('password'):
            user['password'] = request.data.get('password')
        role = user.get('role')
        email = user.get('email')
        phones = request.data.getlist('phones')
        documents = request.data.getlist('documents')
        context = {
            'phones': phones,
            'user': user,
            'documents': documents,
            'avatar': request.data.get('avatar'),
            'rating': request.data.get('rating')
        }
        logger.info(f'Registration with email: {email} ({constants.ROLES[0]}) started')
        if role == constants.ROLE_CLIENT:
            serializer = ClientProfileCreateSerializer(data=request.data, context=context)
        elif role == constants.ROLE_MERCHANT:
            serializer = MerchantProfileCreateSerializer(data=request.data, context=context)
        else:
            logger.error(
                f'Registration with email: {email} ({constants.ROLES[0]}) failed. {constants.RESPONSE_INVALID_ROLE}')
            return Response(response.make_messages_new([('role', constants.RESPONSE_INVALID_ROLE)]),
                            status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            try:
                user = MainUser.objects.get(email=email)
            except MainUser.DoesNotExist:
                logger.error(
                    f'Registration with email: {email} ({constants.ROLES[0]})  failed. {constants.RESPONSE_SERVER_ERROR}')
                return Response(response.make_messages_new([('server', constants.RESPONSE_SERVER_ERROR)]),
                                status.HTTP_500_INTERNAL_SERVER_ERROR)
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            data = {
                'token': token,
                'role': user.role
            }
            logger.info(f'Registration with email: {email} ({constants.ROLES[0]}) succeeded')
            activation = UserActivation.objects.filter(email=email).first()
            if activation:
                activation.delete()
            return Response(data, status=status.HTTP_200_OK, headers=headers)
        logger.error(
            f'Registration with email: {email} ({constants.ROLES[0]}) failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def login_regular(self, request, pk=None):
        serializer = UserLoginSerializer(data=request.data)
        logger.info(f'Regular login (email: {request.data.get("email")}): started')
        if serializer.is_valid():
            email = serializer.data.get('email')
            password = serializer.data.get('password')
            if not email:
                logger.error(
                    f'Regular login (email: {request.data.get("email")}): failed. {constants.RESPONSE_ENTER_EMAIL_OR_PHONE}')
                return Response(response.make_messages_new([('email', constants.RESPONSE_ENTER_EMAIL_OR_PHONE)]),
                                status.HTTP_400_BAD_REQUEST)
            if email:
                try:
                    user = MainUser.objects.get(email=email)
                except MainUser.DoesNotExist:
                    try:
                        phone = MerchantPhone.objects.get(phone=email)
                        if phone.is_valid:
                            user = phone.user
                        else:
                            raise Exception()
                    except:
                        logger.error(
                            f'Regular login (email: {request.data.get("email")}): failed. {constants.RESPONSE_USER_EMAIL_NOT_EXIST}')
                        return Response(
                            response.make_messages_new([('email', constants.RESPONSE_USER_EMAIL_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST
                        )
            if user.check_password(password):
                payload = jwt_payload_handler(user)
                token = jwt_encode_handler(payload)
                data = {
                    'token': token
                }
                logger.info(f'Regular login (email: {request.data.get("email")}): succeeded')
                return Response(data, status.HTTP_200_OK)
            logger.error(
                f'Regular login (email: {request.data.get("email")}): failed. {constants.PASSWORD} {constants.INCORRECT}')
            return Response(
                response.make_messages_new([('password', constants.INCORRECT)]),
                status.HTTP_400_BAD_REQUEST
            )
        logger.error(
            f'Regular login (email: {request.data.get("email")}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], name='send-activation-email')
    def send_activation_email(self, request, pk=None):
        email = request.data.get('email')
        role = request.data.get('role')
        name = request.data.get('name')
        logger.info(f'Activation email sending ({email}): started')
        if email and role:
            try:
                MainUser.objects.get(email=email)
                logger.error(f'Activation email sending ({email}): failed. {constants.RESPONSE_USER_EXISTS}')
                return Response(
                    response.make_messages_new([('user', constants.RESPONSE_USER_EXISTS)]),
                    status.HTTP_400_BAD_REQUEST
                )
            except:
                pass
            if UserActivation.objects.filter(email=email).count() == 0:
                activation = UserActivation.objects.create(email=email, role=role, name=name)
                activation._request = request
                activation._created = True
                activation.save()
                logger.info(f'Activation email sending ({email}): succeeded')
                return Response(status.HTTP_200_OK)
            else:
                activation = UserActivation.objects.filter(email=email, is_active=True).first()
                if activation:
                    if activation.user:
                        logger.error(f'Activation email sending ({email}): failed. {constants.RESPONSE_USER_EXISTS}')
                        return Response(
                            response.make_messages_new([('user', constants.RESPONSE_USER_EXISTS)]),
                            status.HTTP_400_BAD_REQUEST
                        )
                    activation.delete()
                activation = UserActivation.objects.create(email=email, role=role)
                activation._request = request
                activation._created = True
                activation.save()
                logger.info(f'Activation email sending ({email}): succeeded')
                return Response(status.HTTP_200_OK)
        if not email and not role:
            logger.error(
                f'Activation email sending: failed. ({response.missing_field("Email"), response.missing_field("Роль")}')
            return Response(
                response.make_messages_new(
                    [('email', response.missing_field('Email')), ('role', response.missing_field("Роль"))]
                ),
                status.HTTP_400_BAD_REQUEST
            )
        if not email:
            logger.error(f'Activation email sending: failed. {response.missing_field("Email")}')
            return Response(response.make_messages_new([('email', response.missing_field('Email'))]),
                            status.HTTP_400_BAD_REQUEST)
        if not role:
            logger.error(f'Activation email sending ({email}): failed. {response.missing_field("Роль")}')
            return Response(response.make_messages_new([('role', response.missing_field("Роль"))]),
                            status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], name='verify-email')
    def verify_email(self, request, pk=None):
        email = encryption.decrypt(pk)
        logger.info(f'Email verification ({email}): started')
        activation = UserActivation.objects.filter(email=email).first()
        if not activation:
            logger.error(f'Email verification ({email}): failed')
            return redirect('https://docs.djangoproject.com/en/3.0/topics/http/shortcuts/')
        if activation.is_active:
            activation.is_active = False
            logger.info(f'Email verification ({email}): success')
            if activation.role == constants.ROLE_CLIENT:
                return redirect(f'http://istokhome.com/registration-users?email={email}')
            elif activation.role == constants.ROLE_MERCHANT:
                return redirect(f'http://istokhome.com/registration-specials?email={email}')
        logger.error(f'Email verification ({email}): failed')
        return redirect(f'https://istokhome.com/registration-specials?role={activation.role}&email={email}')

    @action(detail=False, methods=['post'])
    def verify_phone(self, request, pk=None):
        code = randrange(1000, 10000)
        while CodeVerification.objects.filter(code=code, phone__is_valid=True).count() > 0:
            code = randrange(1000, 10000)
        data = request.data
        data['code'] = f'{code}'
        data['code'] = f'{1111}'
        serializer = CodeVerificationSerializer(data=data)
        logger.info(f'Phone verification ({request.data.get("phone").get("phone")}): started')
        if serializer.is_valid():
            try:
                phone = MerchantPhone.objects.get(phone=serializer.validated_data.get('phone').get('phone'))
                if phone.is_valid:
                    logger.error(
                        f'Phone verification ({request.data.get("phone").get("phone")}): failed. {constants.RESPONSE_PHONE_ALREADY_REGISTERED}')
                    return Response(
                        response.make_messages_new([('phone', constants.RESPONSE_PHONE_ALREADY_REGISTERED)]),
                        status.HTTP_400_BAD_REQUEST
                    )
            except:
                pass
            try:
                verification = CodeVerification.objects.get(
                    phone__phone=serializer.validated_data.get('phone').get('phone'))
                verification.delete()
            except:
                pass
            serializer.save()
            logger.info(f'Phone verification ({request.data.get("phone").get("phone")}): succeeded')
            return Response(status=status.HTTP_200_OK)
        try:
            message = serializer.errors.get('phone').get('phone').get('messages')[0]
            logger.error(
                f'Phone verification ({request.data.get("phone").get("phone")}): failed. {response.make_messages_new([("phone", message)])}')
            return Response(response.make_messages_new([('phone', message)]), status.HTTP_400_BAD_REQUEST)
        except:
            logger.error(
                f'Phone verification ({request.data.get("phone").get("phone")}): failed. {response.make_errors_new(serializer)}')
            return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def send_code(self, request, pk=None):
        serializer = CodeVerificationSerializer(data=request.data)
        logger.info(f'Send code ({request.data.get("phone").get("phone")}): started')
        if serializer.is_valid():
            try:
                verification = CodeVerification.objects.get(
                    phone__phone=serializer.validated_data.get('phone').get('phone'))
                if verification.code != serializer.validated_data.get('code'):
                    logger.error(
                        f'Send code ({request.data.get("phone").get("phone")}): failed. {constants.RESPONSE_VERIFICATION_INVALID_CODE}')
                    return Response(
                        response.make_messages_new(
                            [('verification code', constants.RESPONSE_VERIFICATION_INVALID_CODE)]
                        ),
                        status.HTTP_400_BAD_REQUEST
                    )
                to_tz = timezone.get_default_timezone()
                time_diff = verification.creation_date.astimezone(to_tz) - datetime.now().astimezone(to_tz)
                if (time_diff.days * 24 * 60) > 15:
                    logger.error(
                        f'Send code ({request.data.get("phone").get("phone")}): failed. {constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST}')
                    return Response(
                        response.make_messages_new(
                            [('verification code', constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST)]
                        ),
                        status.HTTP_400_BAD_REQUEST
                    )
            except CodeVerification.DoesNotExist:
                logger.error(
                    f'Send code ({request.data.get("phone").get("phone")}): failed. {constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST}')
                return Response(
                    response.make_messages_new(
                        [('verification code', constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST)]
                    ),
                    status.HTTP_400_BAD_REQUEST
                )
            verification.delete()
            merchant_phone = verification.phone
            merchant_phone.is_valid = True
            merchant_phone.save()
            data = {
                'phone': serializer.data.get('phone').get('phone')
            }
            logger.info(f'Send code ({request.data.get("phone").get("phone")}): succeeded')
            return Response(data, status=status.HTTP_200_OK)
        logger.error(
            f'Send code ({request.data.get("phone").get("phone")}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def social_login(self, request, pk=None):
        social_type = request.data.get('social_type')
        access_token = request.data.get('access_token')
        role = request.data.get('role')
        social_list = [constants.FACEBOOK, constants.GOOGLE, constants.VK_WEB]
        role_list = [constants.ROLE_CLIENT, constants.ROLE_MERCHANT]
        info, error = oauth.get_social_info(request.data, social_type)

        logger.info(f'Social login ({social_type}): started')
        if not social_type or not access_token or not role:
            logger.error(f'Social login ({social_type}): failed. {constants.RESPONSE_EMPTY_INPUT_DATA}')
            return Response(
                response.make_messages_new([('social_login', constants.RESPONSE_EMPTY_INPUT_DATA)]),
                status.HTTP_400_BAD_REQUEST
            )
        if social_type not in social_list or role not in role_list:
            logger.error(f'Social login ({social_type}): failed. {constants.RESPONSE_INCORRECT_INPUT_DATA}')
            return Response(
                response.make_messages_new([('social_login', constants.RESPONSE_INCORRECT_INPUT_DATA)]),
                status.HTTP_400_BAD_REQUEST
            )
        if not info:
            logger.error(f'Social login ({social_type}): failed. {constants.RESPONSE_SERVER_ERROR}')
            return Response(response.make_messages_new([('server', error)]), status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            if MainUser.objects.filter(email=info['email']).count() > 0:
                user = MainUser.objects.get(email=info['email'])
            else:
                phone = MerchantPhone.objects.get(phone=info['phone'])
                user = phone.user
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
            data = {
                'register': False,
                'token': token
            }
            logger.info(f'Social login ({social_type}): succeeded')
            return Response(data, status.HTTP_200_OK)
        except:
            role = request.data.get('role')
            if not role:
                logger.error(f'Social login ({social_type}): failed. {constants.RESPONSE_ENTER_ROLE}')
                return Response(response.make_messages([('role', constants.RESPONSE_ENTER_ROLE)]),
                                status.HTTP_400_BAD_REQUEST)
            if role == constants.ROLE_CLIENT and info.get('email') and info.get('first_name') and info.get('birthday'):
                user = {
                    'email': info['email'],
                    'role': int(request.data.get('role'))
                }
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
                logger.error(f'Social login ({social_type}): failed. {response.make_errors_new(serializer)}')
                return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)
            info['register'] = True
        logger.info(f'Social login ({social_type}): succeeded')
        return Response(info, status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def top_details(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages_new([('user', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages_new([('user', constants.RESPONSE_USER_NOT_MERCHANT)]),
                            status.HTTP_400_BAD_REQUEST)
        context = {
            'request': request
        }
        from_project = request.data.get('from_project')
        if from_project:
            try:
                project = Project.objects.get(id=from_project)
            except:
                return Response(response.make_messages_new([('project', constants.RESPONSE_DOES_NOT_EXIST)]),
                                status.HTTP_400_BAD_REQUEST)
            project.to_profile_count += 1
            project.save()
        serializer = UserTopDetailSerializer(user, context=context)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def projects(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages_new([('user', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages_new([('user', constants.RESPONSE_USER_NOT_MERCHANT)]))
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
            return Response(response.make_messages_new([('user', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages_new([('user', constants.RESPONSE_USER_NOT_MERCHANT)]))
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
            return Response(response.make_messages_new([('user', constants.RESPONSE_DOES_NOT_EXIST)]))
        if user.role == constants.ROLE_CLIENT:
            return Response(response.make_messages_new([('user', constants.RESPONSE_USER_NOT_MERCHANT)]))
        serializer = MerchantDetailSerializer(user, context=request)
        return Response(serializer.data)


class ProjectReview(viewsets.GenericViewSet):
    queryset = MerchantReview.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        logger.info(f'Like of merchant review ({pk}) by user ({request.user.email}): started')
        try:
            review = MerchantReview.objects.get(id=pk)
        except MerchantReview.DoesNotExist:
            logger.error(
                f'Like of merchant review ({pk}) by user ({request.user.email}): failed. Обзор {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('review', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]),
                            status.HTTP_400_BAD_REQUEST)
        try:
            review.user_likes.get(id=request.user.id)
            review.user_likes.remove(request.user)
            review.likes_count = review.likes_count - 1
            review.save()
        except:
            review.user_likes.add(request.user)
            review.likes_count = review.likes_count + 1
            review.save()
        logger.info(f'Like of merchant review ({pk}) by user ({request.user.email}): succeeded')
        return Response(status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complain(self, request, pk=None):
        logger.info(f'Complain to merchant review ({pk}) by user ({request.user.email}): started')
        try:
            review = self.queryset.get(id=pk)
        except MerchantReview.DoesNotExist:
            logger.error(
                f'Complain to merchant review ({pk}) by user ({request.user.email}): failed. Обзор {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('review', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]),
                            status.HTTP_400_BAD_REQUEST)
        serializer = ReviewComplainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, review=review)
            logger.info(f'Complain to merchant review ({pk}) by user ({request.user.email}): succeeded')
            return Response(serializer.data, status.HTTP_200_OK)
        logger.error(
            f'Complain to merchant review ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)


class ReviewReplyViewSet(viewsets.GenericViewSet):
    queryset = ReviewReply.objects.all()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def complain(self, request, pk=None):
        logger.info(f'Complain to review reply ({pk}) by user ({request.user.email}): started')
        try:
            reply = self.queryset.get(id=pk)
        except ReviewReply.DoesNotExist:
            logger.error(
                f'Complain to review reply ({pk}) by user ({request.user.email}): failed. Ответ {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('reply', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]),
                            status.HTTP_400_BAD_REQUEST)
        serializer = ReviewReplyComplainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, reply=reply)
            logger.info(f'Complain to review reply ({pk}) by user ({request.user.email}): succeeded')
            return Response(serializer.data, status.HTTP_200_OK)
        logger.error(
            f'Complain to review reply ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)


class RegisterPage(views.APIView):
    def get(self, request):
        # tags = ProjectTag.objects.all()
        # tags_serializer = ProjectTagShortSerializer(tags, many=True)
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
        }
        return Response(data)
