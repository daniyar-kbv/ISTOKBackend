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
    MerchantProfileUpdate, GetStatiscticsInSerialzier, GetStatiscticsOutSerialzier
from users.serializers import PhoneSerializer, ClientRatingCreateSerializer, MerchantReviewCreateSerializer, \
    MerchantReviewDetailList, MerchantReviewReplyCreateSerializer
from users.models import MainUser, MerchantPhone, MerchantReview, ReviewReply
from profiles.models import FormQuestionGroup, Application, ApplicationDocument, Notification
from profiles.serializers import FormQuestionGroupSerializer, NotificationSerializer
from payments.models import PaidFeatureType, Transaction, UsersPaidFeature, ProjectPaidFeature
from main.models import Project, ProjectType, ProjectStyle, ProjectPurpose, ProjectCategory, ProjectView, ProjectComment, \
    ProjectCommentReply
from main.serializers import ProjectProfileGetSerializer, ProjectCreateSerializer, ProjectDetailSerializer, \
    ProjectUpdateSerializer, ProjectPromotionSerializer, ProjectForUpdateSerializer, ProjectCategoryShortSerializer, \
    ProjectPurposeShortSerializer, ProjectTypeSerializer, ProjectStyleSerializer, \
    ProjectCategorySpecializationSerializer, ProjectSearchSerializer, ProjectShortSerializer, \
    ProjectCommentReplyCreateSerializer
from main.tasks import deactivate_user_feature, deactivate_project_feature, notify_user_feature, notify_project_feature
from utils import response, pagination
from utils.permissions import IsClient, IsAuthenticated, IsMerchant, HasPhone
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
import constants, logging

logger = logging.getLogger(__name__)
jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER


class ProfileViewSet(viewsets.GenericViewSet,
                     mixins.UpdateModelMixin):
    queryset = MainUser.objects.all()
    permission_classes = (permissions.IsAuthenticated, )

    @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request, pk=None):
        user = request.user
        if request.method == 'GET':
            if user.role == constants.ROLE_CLIENT:
                serializer = ClientProfileGetSerializer(user, context=request)
                return Response(serializer.data)
            elif user.role == constants.ROLE_MERCHANT:
                serializer = MerchantProfileGetSerializer(user, context=request)
                return Response(serializer.data)
        if request.method == 'PUT':
            logger.info(f'Edit profile by user ({request.user.email}): started')
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
                    logger.info(f'Edit profile by user ({request.user.email}): succeeded')
                    return Response(serializer.data, status.HTTP_200_OK)
                logger.error(
                    f'Edit profile by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
                return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)
            elif user.role == constants.ROLE_MERCHANT:
                request.data._mutable = True
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
                            logger.error(
                                f'Edit profile by user ({request.user.email}): failed. {constants.RESPONSE_MAX_FILES} 6')
                            return Response(
                                response.make_messages_new([('total_documents', f'{constants.RESPONSE_MAX_FILES} 6')]),
                                status.HTTP_400_BAD_REQUEST
                            )
                    except:
                        logger.error(
                            f'Edit profile by user ({request.user.email}): failed. {constants.RESPONSE_RIGHT_ONLY_DIGITS}')
                        return Response(
                            response.make_messages_new([('total_documents', constants.RESPONSE_RIGHT_ONLY_DIGITS)]),
                            status.HTTP_400_BAD_REQUEST
                        )
                else:
                    logger.error(
                        f'Edit profile by user ({request.user.email}): failed. {constants.RESPONSE_FIELD_REQUIRED}')
                    return Response(
                        response.make_messages_new([('total_documents', constants.RESPONSE_FIELD_REQUIRED)]),
                        status.HTTP_400_BAD_REQUEST
                    )
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
                    logger.info(f'Edit profile by user ({request.user.email}): succeeded')
                    return Response(data)
                logger.error(
                    f'Edit profile by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
                return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request, pk=None):
        user = request.user
        logger.info(f'Change password by user ({request.user.email}): started')
        serializer = UserChangePasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'Change password by user ({request.user.email}): succeeded')
            return Response(serializer.data, status.HTTP_200_OK)
        logger.error(f'Change password by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get', 'post'], permission_classes=[IsClient])
    def client_form(self, request, pk=None):
        if request.method == 'GET':
            groups = FormQuestionGroup.objects.all().order_by('position')
            serializer = FormQuestionGroupSerializer(groups, many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            logger.info(f'Send client form by user ({request.user.email}): started')
            serializer = FormUserAnswerCreatePostSerializer(data=request.data, context=request)
            if serializer.is_valid():
                serializer.save()
                logger.info(f'Send client form by user ({request.user.email}): succeeded')
                return Response(status=status.HTTP_200_OK)
            logger.error(
                f'Send client form by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
            return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def client(self, request, pk=None):
        try:
            user = MainUser.objects.get(id=pk)
        except MainUser.DoesNotExist:
            return Response(response.make_messages_new([('user', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]),
                            status.HTTP_400_BAD_REQUEST)
        if user.role == constants.ROLE_MERCHANT:
            return Response(response.make_messages_new([('user', constants.RESPONSE_USER_NOT_CLIENT)]),
                            status.HTTP_400_BAD_REQUEST)
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
        categories = ProjectCategory.objects.all()
        categories_json = []
        for category in categories:
            if category.specializations.all().count() > 0:
                for specialization in category.specializations.all():
                    categories_serializer = ProjectCategorySpecializationSerializer(category, context=specialization)
                    categories_json.append(categories_serializer.data)
            else:
                categories_serializer = ProjectCategorySpecializationSerializer(category, context=None)
                categories_json.append(categories_serializer.data)
        data = {
            'profile': serializer.data,
            'categories': categories_json
        }
        return Response(data)

    @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated, IsMerchant])
    def projects(self, request, pk=None):
        if request.method == 'GET':
            projects = Project.objects.filter(user=request.user)
            serializer = ProjectProfileGetSerializer(projects, many=True, context=request)
            return Response(serializer.data)
        elif request.method == 'POST':
            logger.info(f'Create project by user ({request.user.email}): started')
            context = {
                'render': request.data.get('render')
            }
            if request.data.get('documents'):
                context['documents'] = request.data.pop('documents')
                if len(context['documents']) > 12:
                    logger.error(
                        f'Create project by user ({request.user.email}): failed. {constants.RESPONSE_MAX_FILES} 12')
                    return Response(
                        response.make_messages_new([('total_documents', f'{constants.RESPONSE_MAX_FILES} 12')])
                    )
            serializer = ProjectCreateSerializer(data=request.data, context=context)
            if serializer.is_valid():
                serializer.save(user=request.user)
                logger.info(f'Create project by user ({request.user.email}): succeeded')
                return Response(serializer.data)
            logger.error(
                f'Create project by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
            return Response(response.make_errors_new(serializer), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'put', 'delete'], permission_classes=[IsAuthenticated, IsMerchant])
    def project(self, request, pk=None):
        logger.info(f'Open/edit/delete project ({pk}) by user ({request.user.email}): started')
        try:
            project = Project.objects.get(id=pk)
        except:
            logger.error(
                f'Open/edit/delete project ({pk}) by user ({request.user.email}): failed. Проект {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('project', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if project.user != request.user:
            logger.error(
                f'Open/edit/delete project ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} проекта')
            return Response(response.make_messages_new([('project', constants.RESPONSE_NOT_OWNER)]),
                            status.HTTP_400_BAD_REQUEST)
        if request.method == 'GET':
            serializer = ProjectDetailSerializer(project, context=request)
            return Response(serializer.data)
        elif request.method == 'PUT':
            documents = []
            if request.data.get('documents'):
                documents = request.data.pop('documents')
            delete_documents = []
            if request.data.get('delete_documents'):
                delete_documents = request.data.pop('delete_documents')
            total_documents = request.data.get('total_documents')
            if total_documents:
                try:
                    if int(total_documents) > 12:
                        logger.error(
                            f'Edit project ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_MAX_FILES} 12')
                        return Response(
                            response.make_messages_new([('total_documents', f'{constants.RESPONSE_MAX_FILES} 12')]),
                            status.HTTP_400_BAD_REQUEST
                        )
                except:
                    logger.error(
                        f'Edit project ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_RIGHT_ONLY_DIGITS}')
                    return Response(
                        response.make_messages_new([('total_documents', constants.RESPONSE_RIGHT_ONLY_DIGITS)]),
                        status.HTTP_400_BAD_REQUEST
                    )
            else:
                logger.error(
                    f'Edit project ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_FIELD_REQUIRED}')
                return Response(response.make_messages_new([('total_documents', constants.RESPONSE_FIELD_REQUIRED)]),
                                status.HTTP_400_BAD_REQUEST)
            context = {
                'documents': documents,
                'delete_documents': delete_documents,
                'render': request.data.get('render')
            }
            serializer = ProjectUpdateSerializer(project, data=request.data, context=context)
            if serializer.is_valid():
                serializer.save()
                logger.info(f'Edit project ({pk}) by user ({request.user.email}): succeeded')
                return Response(serializer.data)
            logger.error(
                f'Edit project ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
            return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            logger.info(f'Delete project ({pk}) by user ({request.user.email}): started')
            project.delete()
            logger.info(f'Delete project ({pk}) by user ({request.user.email}): succeeded')
            return Response(status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
    def project_for_update(self, request, pk=None):
        try:
            project = Project.objects.get(id=pk)
        except:
            return Response(response.make_messages_new([('project', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if project.user != request.user:
            return Response(response.make_messages_new([('project', constants.RESPONSE_NOT_OWNER)]),
                            status.HTTP_400_BAD_REQUEST)
        project_serializer = ProjectForUpdateSerializer(project, context=request)
        categories = ProjectCategory.objects.all()
        category_serializer = ProjectCategoryShortSerializer(categories, many=True)
        purposes = ProjectPurpose.objects.all()
        purpose_serializer = ProjectPurposeShortSerializer(purposes, many=True)
        types = ProjectType.objects.all()
        type_serializer = ProjectTypeSerializer(types, many=True)
        styles = ProjectStyle.objects.all()
        style_serializer = ProjectStyleSerializer(styles, many=True)
        data = {
            'project': project_serializer.data,
            'categories': category_serializer.data,
            'purposes': purpose_serializer.data,
            'styles': style_serializer.data,
            'types': type_serializer.data
        }
        return Response(data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
    def promoted(self, request, pk=None):
        user = request.user
        features = ProjectPaidFeature.objects.filter(project__user=user)
        data = []
        for feature in features:
            context = {
                'type': feature.type.type,
                'request': request
            }
            serializer = ProjectPromotionSerializer(feature.project, context=context)
            data.append(serializer.data)
        return Response(data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
    def project_for_promotion(self, request, pk=None):
        if pk != 'none':
            try:
                project = Project.objects.get(id=pk)
            except:
                return Response(response.make_messages_new([('project', constants.RESPONSE_DOES_NOT_EXIST)]),
                                status.HTTP_400_BAD_REQUEST)
        else:
            projects = Project.objects.filter(user=request.user)
            if projects.count() > 0:
                project = projects.first()
            else:
                return Response(constants.RESPONSE_NO_PROJECTS, status.HTTP_400_BAD_REQUEST)
        if project.user != request.user:
            return Response(response.make_messages_new([('project', constants.RESPONSE_NOT_OWNER)]),
                            status.HTTP_400_BAD_REQUEST)
        project_serializer = ProjectSearchSerializer(project, context=request)
        projects = Project.objects.filter(user=request.user)
        projects_serializer = ProjectShortSerializer(projects, many=True)
        data = {
            'current_project': project_serializer.data,
            'projects': projects_serializer.data
        }
        return Response(data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
    def statistics(self, request, pk=None):
        try:
            feature = ProjectPaidFeature.objects.get(id=pk)
        except:
            return Response(response.make_messages_new([('feature', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if feature.project.user != request.user:
            return Response(response.make_messages_new([('feature', constants.RESPONSE_NOT_OWNER)]),
                            status.HTTP_400_BAD_REQUEST)
        serializer = GetStatiscticsInSerialzier(data=request.data)
        if serializer.is_valid():
            type = serializer.data.get('type')
            time_period = serializer.data.get('time_period')
            if time_period == constants.STATISTICS_TIME_7_DAYS:
                days = 7
            elif time_period == constants.STATISTICS_TIME_30_DAYS:
                days = 30
            today = datetime.today()
            statistics_data = []
            for day in range(days):
                with_delta = today - timedelta(days=day)
                if type == constants.STATISTICS_TYPE_VIEWS:
                    statistics_data.append({
                        "date": with_delta.strftime(constants.DATE_FORMAT),
                        "count": ProjectView.objects.filter(project=feature.project, creation_date__day=with_delta.day,
                                                            creation_date__month=with_delta.month).count()
                    })
                if type == constants.STATISTICS_TYPE_APPS:
                    statistics_data.append({
                        "date": with_delta.strftime(constants.DATE_FORMAT),
                        "count": Application.objects.filter(project=feature.project,
                                                            creation_date__day=with_delta.day,
                                                            creation_date__month=with_delta.month).count()
                    })
            project_serializer = GetStatiscticsOutSerialzier(feature)
            data = {
                'project_data': project_serializer.data,
                'statistics_data': statistics_data
            }
            return Response(data, status.HTTP_200_OK)
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
    def get_reviews(self, request, pk=None):
        user = request.user
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

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
    def delete_review(self, request, pk=None):
        logger.info(f'Delete review ({pk}) by user ({request.user.email}): started')
        try:
            review = MerchantReview.objects.get(id=pk)
        except:
            logger.error(
                f'Delete review ({pk}) by user ({request.user.email}): failed. Отзыв {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('review', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]),
                            status.HTTP_400_BAD_REQUEST)
        user = request.user
        if review.merchant != user:
            logger.error(
                f'Delete review ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} обзора')
            return Response(constants.RESPONSE_NOT_OWNER, status.HTTP_400_BAD_REQUEST)
        review.delete()
        logger.info(f'Delete review ({pk}) by user ({request.user.email}): succeeded')
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMerchant])
    def review_reply(self, request, pk=None):
        logger.info(f'Reply to review ({pk}) by user ({request.user.email}): started')
        try:
            review = MerchantReview.objects.get(id=pk)
        except:
            logger.error(
                f'Reply to review ({pk}) by user ({request.user.email}): failed. Отзыв {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('review', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]),
                            status.HTTP_400_BAD_REQUEST)
        try:
            ReviewReply.objects.get(review=review)
            logger.error(
                f'Reply to review ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_REPLY_EXISTS}')
            return Response(response.make_messages_new([('review_reply', constants.RESPONSE_REPLY_EXISTS)]))
        except:
            pass
        user = request.user
        if review.merchant != user:
            logger.error(
                f'Reply to review ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} обзора')
            return Response(constants.RESPONSE_NOT_OWNER, status.HTTP_400_BAD_REQUEST)
        context = {
            'user': user
        }
        if request.data.get('documents'):
            documents = request.data.pop('documents')
            context['documents'] = documents
        serializer = MerchantReviewReplyCreateSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save(review=review, user=user)
            logger.info(f'Reply to review ({pk}) by user ({request.user.email}): succeeded')
            return Response(serializer.data, status.HTTP_200_OK)
        logger.error(
            f'Reply to review ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
    def delete_review_reply(self, request, pk=None):
        logger.info(f'Delete review reply ({pk}) by user ({request.user.email}): started')
        try:
            reply = ReviewReply.objects.get(id=pk)
        except:
            logger.error(
                f'Delete review reply ({pk}) by user ({request.user.email}): failed. Ответ {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('review_reply', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]),
                            status.HTTP_400_BAD_REQUEST)
        user = request.user
        if reply.user != user:
            logger.error(
                f'Delete review reply ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} ответа')
            return Response(constants.RESPONSE_NOT_OWNER, status.HTTP_400_BAD_REQUEST)
        reply.delete()
        logger.info(f'Delete review reply ({pk}) by user ({request.user.email}): succeeded')
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMerchant])
    def comment_reply(self, request, pk=None):
        logger.info(f'Reply to comment ({pk}) by user ({request.user.email}): started')
        try:
            comment = ProjectComment.objects.get(id=pk)
        except ProjectComment.DoesNotExist:
            logger.error(
                f'Reply to comment ({pk}) by user ({request.user.email}): failed. Комментарий {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('comment', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if comment.project.user != request.user:
            logger.error(
                f'Reply to comment ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} проекта')
            return Response(response.make_messages_new([('project', constants.RESPONSE_NOT_OWNER)]))
        try:
            ProjectCommentReply.objects.get(comment=comment)
            logger.error(
                f'Reply to comment ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_COMMENT_REPLY_EXISTS}')
            return Response(response.make_messages_new([('comment_reply', constants.RESPONSE_COMMENT_REPLY_EXISTS)]))
        except:
            pass
        context = {}
        if request.data.get('documents'):
            documents = request.data.pop('documents')
            context['documents'] = documents
        serializer = ProjectCommentReplyCreateSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save(comment=comment, user=request.user)
            logger.info(f'Reply to comment ({pk}) by user ({request.user.email}): succeeded')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(
            f'Reply to comment ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
    def delete_comment(self, request, pk=None):
        logger.info(f'Delete comment ({pk}) by user ({request.user.email}): started')
        try:
            comment = ProjectComment.objects.get(id=pk)
        except ProjectComment.DoesNotExist:
            logger.error(
                f'Delete comment ({pk}) by user ({request.user.email}): failed. Комментарий {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('comment', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if comment.project.user != request.user:
            logger.error(
                f'Delete comment ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} проекта')
            return Response(response.make_messages_new([('project', constants.RESPONSE_NOT_OWNER)]))
        comment.delete()
        logger.info(f'Delete comment ({pk}) by user ({request.user.email}): succeeded')
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
    def delete_comment_reply(self, request, pk=None):
        logger.info(f'Delete comment reply ({pk}) by user ({request.user.email}): started')
        try:
            reply = ProjectCommentReply.objects.get(id=pk)
        except ProjectCommentReply.DoesNotExist:
            logger.error(
                f'Delete comment reply ({pk}) by user ({request.user.email}): failed. Ответ {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('reply', constants.RESPONSE_DOES_NOT_EXIST)]),
                            status.HTTP_400_BAD_REQUEST)
        if reply.user != request.user:
            logger.error(
                f'Delete comment reply ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} ответа')
            return Response(response.make_messages_new([('comment_reply', constants.RESPONSE_NOT_OWNER)]))
        reply.delete()
        logger.info(f'Delete comment reply ({pk}) by user ({request.user.email}): succeeded')
        return Response(status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def notifications(self, request, pk=None):
        user = request.user
        notifications = Notification.objects.filter(user=user)
        paginator = pagination.CustomPagination()
        paginator.page_size = 13
        page = paginator.paginate_queryset(notifications, request)
        if page is not None:
            serializer = NotificationSerializer(notifications, many=True)
            return paginator.get_paginated_response(serializer.data)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def read_notification(self, request, pk=None):
        logger.info(f'Read notification ({pk}) by user ({request.user.email}): started')
        try:
            notification = Notification.objects.get(id=pk)
        except:
            logger.error(
                f'Read notification ({pk}) by user ({request.user.email}): failed. Уведомление {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('notification', constants.RESPONSE_DOES_NOT_EXIST)]))
        if notification.user != request.user:
            logger.error(
                f'Read notification ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_NOT_OWNER} уведомления')
            return Response(response.make_messages_new([('notification', constants.RESPONSE_NOT_OWNER)]))
        notification.read = True
        notification.save()
        logger.info(f'Read notification ({pk}) by user ({request.user.email}): succeeded')
        return Response(status=status.HTTP_200_OK)


class IsPhoneValidView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    http_method_names = ['post']
    parser_classes = (FormParser, MultiPartParser, JSONParser,)

    def post(self, request, format=None):
        phone = request.data.get('phone')
        serializer = PhoneSerializer(data={
            'phone': phone
        })
        logger.info(f'Validation of phone ({phone}) by user ({request.user.email}): started')
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
                        logger.error(
                            f'Validation of phone ({phone}) by user ({request.user.email}): failed. {constants.RESPONSE_PHONE_REGISTERED}')
                        return Response(response.make_messages_new([('phone', constants.RESPONSE_PHONE_REGISTERED)]))
            data = {
                'is_valid': is_valid
            }
            logger.info(f'Validation of phone ({phone}) by user ({request.user.email}): succeeded')
            return Response(data)
        logger.error(
            f'Validation of phone {phone} by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)


class ApplicationViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin):
    queryset = Application.objects.all()
    permission_classes = [IsAuthenticated, ]

    def list(self, request, *args, **kwargs):
        status_name = request.GET.get('status') if request.GET.get('status') else constants.APPLICATION_CONFIRMED_STRING
        user = request.user

        if user.role == constants.ROLE_CLIENT and status_name not in constants.CLIENT_STATUSES:
            return Response(response.make_messages([constants.RESPONSE_STATUS_NOT_VALID]), status.HTTP_400_BAD_REQUEST)
        elif user.role == constants.ROLE_MERCHANT and status_name not in constants.MERCHANT_STATUSES:
            return Response(response.make_messages([constants.RESPONSE_STATUS_NOT_VALID]), status.HTTP_400_BAD_REQUEST)

        if user.role == constants.ROLE_CLIENT:
            queryset = self.get_queryset().filter(client=user)
        elif user.role == constants.ROLE_MERCHANT:
            queryset = self.get_queryset().filter(merchant=user)

        data = {
            'confirmed_count': queryset.filter(status=constants.APPLICATION_CONFIRMED).count(),
            'finished_count': queryset.filter(status=constants.APPLICATION_FINISHED_CONFIRMED).count(),
            'declined_couresponse.missing_fieldnt': queryset.filter(Q(status=constants.APPLICATION_DECLINED_CLIENT) |
                                              Q(status=constants.APPLICATION_DECLINED_MERCHANT)).count()
        }

        if user.role == constants.ROLE_CLIENT:
            data['waiting_count'] = queryset.filter(Q(status=constants.APPLICATION_CREATED) |
                                                    Q(status=constants.APPLICATION_FINISHED)).count()
        elif user.role == constants.ROLE_MERCHANT:
            data['new'] = queryset.filter(status=constants.APPLICATION_CREATED).count()
            data['waiting_count'] = queryset.filter(status=constants.APPLICATION_FINISHED).count()

        if status_name == constants.APPLICATION_NEW_STRING:
            queryset = queryset.filter(status=constants.APPLICATION_CREATED)
            serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
        elif status_name == constants.APPLICATION_CONFIRMED_STRING:
            queryset = queryset.filter(status=constants.APPLICATION_CONFIRMED)
            if user.role == constants.ROLE_CLIENT:
                serializer_class = ApplicationClientConfirmedSerializer
            elif user.role == constants.ROLE_MERCHANT:
                serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
        elif status_name == constants.APPLICATION_WAITING_STRING:
            if user.role == constants.ROLE_CLIENT:
                queryset = queryset.filter(Q(status=constants.APPLICATION_CREATED) |
                                           Q(status=constants.APPLICATION_FINISHED))
            elif user.role == constants.ROLE_MERCHANT:
                queryset = queryset.filter(status=constants.APPLICATION_FINISHED)
            serializer_class = ApplicationBaseSerializer
        elif status_name == constants.APPLICATION_FINISHED_STRING:
            queryset = queryset.filter(status=constants.APPLICATION_FINISHED_CONFIRMED)
            if user.role == constants.ROLE_CLIENT:
                serializer_class = ApplicationClientFinishedSerializer
            elif user.role == constants.ROLE_MERCHANT:
                serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
        elif status_name == constants.APPLICATION_DECLINED_STRING:
            queryset = queryset.filter(Q(status=constants.APPLICATION_DECLINED_CLIENT) |
                                                  Q(status=constants.APPLICATION_DECLINED_MERCHANT))
            serializer_class = ApplicationDeclinedSerializer

        paginator = pagination.CustomPagination()
        paginator.page_size = 2
        page = paginator.paginate_queryset(queryset, request=request)

        if page is not None:
            serializer = serializer_class(page, many=True, context=request)
            return paginator.get_paginated_response(serializer.data, additional_data=data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = ApplicationDetailSerializer(instance, context=request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def finish(self, request, pk=None):
        logger.info(f'Finish application ({pk}) by user ({request.user.email}): started')
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            logger.error(
                f'Finish application ({pk}) by user ({request.user.email}): failed. Заявка {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('application', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]))
        user = request.user
        if user.role == constants.ROLE_CLIENT:
            if application.client != user:
                logger.error(
                    f'Finish application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_CANT_MODIFY}')
                return Response(response.make_messages_new([('application', constants.RESPONSE_CANT_MODIFY)]))
            if application.status != constants.APPLICATION_CONFIRMED:
                logger.error(
                    f'Finish application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Принятые')
                return Response(
                    response.make_messages_new(
                        [('application', f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Принятые')]
                    ),
                    status.HTTP_400_BAD_REQUEST
                )
            context = {
                'user': user
            }
            if request.data.get('documents'):
                documents = request.data.pop('documents')
                context['documents'] = documents
            serializer = MerchantReviewCreateSerializer(data=request.data, context=context)
            if serializer.is_valid():
                serializer.save(merchant=application.merchant, user=user)
                application.status = constants.APPLICATION_FINISHED
                application.save()
                logger.info(f'Finish application ({pk}) by user ({request.user.email}): succeeded')
                return Response(serializer.data, status.HTTP_200_OK)
            logger.error(
                f'Finish application ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
            return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)
        elif user.role == constants.ROLE_MERCHANT:
            if application.merchant != user:
                logger.error(
                    f'Finish application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_CANT_MODIFY}')
                return Response(response.make_messages_new([('application', constants.RESPONSE_CANT_MODIFY)]))
            if application.status != constants.APPLICATION_CONFIRMED and \
                    application.status != constants.APPLICATION_FINISHED:
                logger.error(
                    f'Finish application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают подтверждения, В процессе')
                return Response(
                    response.make_messages_new(
                        [('application', f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают подтверждения, В процессе')]
                    ),
                    status.HTTP_400_BAD_REQUEST
                )
            serializer = ClientRatingCreateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, client=application.client)
                application.status = constants.APPLICATION_FINISHED_CONFIRMED
                application.save()
                logger.info(f'Finish application ({pk}) by user ({request.user.email}): succeeded')
                return Response(serializer.data, status.HTTP_200_OK)
            logger.error(
                f'Finish application ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
            return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def decline(self, request, pk=None):
        logger.info(f'Decline application ({pk}) by user ({request.user.email}): started')
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            logger.error(
                f'Decline application ({pk}) by user ({request.user.email}): failed. Заявка {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('application', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]))
        user = request.user
        if user.role == constants.ROLE_CLIENT:
            if application.client != user:
                logger.error(
                    f'Decline application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_CANT_MODIFY}')
                return Response(response.make_messages_new([('application', constants.RESPONSE_CANT_MODIFY)]))
            if application.status != constants.APPLICATION_CREATED:
                logger.error(
                    f'Decline application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают ответа')
                return Response(
                    response.make_messages_new(
                        [('application', f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают ответа')]
                    ),
                    status.HTTP_400_BAD_REQUEST
                )
            application.status = constants.APPLICATION_DECLINED_CLIENT
            application.save()
            logger.info(f'Decline application ({pk}) by user ({request.user.email}): succeeded')
            return Response(status=status.HTTP_200_OK)
        elif user.role == constants.ROLE_MERCHANT:
            if application.merchant != user:
                logger.error(
                    f'Decline application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_CANT_MODIFY}')
                return Response(response.make_messages_new([('application', constants.RESPONSE_CANT_MODIFY)]))
            if application.status != constants.APPLICATION_CREATED:
                logger.error(
                    f'Decline application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые')
                return Response(
                    response.make_messages_new(
                        [('application', f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые')]
                    ),
                    status.HTTP_400_BAD_REQUEST
                )
            serializer = ApplicationDeclineSerializer(application, data=request.data)
            if serializer.is_valid():
                serializer.save()
                logger.info(f'Decline application ({pk}) by user ({request.user.email}): succeeded')
                return Response(serializer.data, status.HTTP_200_OK)
            logger.error(
                f'Decline application ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
            return Response(response.make_errors_new(serializer), status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[IsMerchant])
    def accept(self, request, pk=None):
        logger.info(f'Accept application ({pk}) by user ({request.user.email}): started')
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            logger.error(
                f'Accept application ({pk}) by user ({request.user.email}): failed. Заявка {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('application', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]))
        user = request.user
        if application.merchant != user:
            logger.error(
                f'Accept application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_CANT_MODIFY}')
            return Response(response.make_messages_new([('application', constants.RESPONSE_CANT_MODIFY)]))
        if application.status != constants.APPLICATION_CREATED:
            logger.error(
                f'Accept application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые')
            return Response(
                response.make_messages_new(
                    [('application', f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые')]
                ),
                status.HTTP_400_BAD_REQUEST
            )
        application.status = constants.APPLICATION_CONFIRMED
        application.save()
        logger.info(f'Accept application ({pk}) by user ({request.user.email}): succeeded')
        return Response(status.HTTP_200_OK)

    # TODO: add permissions.HasPhone
    @action(detail=True, methods=['post'], permission_classes=[IsClient, ])
    def resend(self, request, pk=None):
        logger.info(f'Resend application ({pk}) by user ({request.user.email}): started')
        try:
            application = Application.objects.get(id=pk)
        except Application.DoesNotExist:
            logger.error(
                f'Resend application ({pk}) by user ({request.user.email}): failed. Заявка {constants.RESPONSE_DOES_NOT_EXIST}')
            return Response(response.make_messages_new([('application', f'{pk} {constants.RESPONSE_DOES_NOT_EXIST}')]))
        user = request.user
        if application.client != user:
            logger.error(
                f'Resend application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_CANT_MODIFY}')
            return Response(response.make_messages_new([('application', constants.RESPONSE_CANT_MODIFY)]))
        if application.status != constants.APPLICATION_FINISHED_CONFIRMED:
            logger.error(
                f'Resend application ({pk}) by user ({request.user.email}): failed. {constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Завершенные')
            return Response(
                response.make_messages_new(
                    [('application', f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Завершенные')]
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
            logger.info(f'Resend application ({pk}) by user ({request.user.email}): succeeded')
            return Response(serializer.data, status=status.HTTP_200_OK)
        logger.error(
            f'Resend application ({pk}) by user ({request.user.email}): failed. {response.make_errors_new(serializer)}')
        return Response(response.make_errors_new(serializer), status=status.HTTP_400_BAD_REQUEST)
