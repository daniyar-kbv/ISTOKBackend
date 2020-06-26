# from rest_framework import viewsets, mixins, status, permissions, views, exceptions
# from rest_framework.response import Response
# from rest_framework.decorators import action
# from rest_framework.parsers import FormParser, MultiPartParser, JSONParser
# from rest_framework_jwt.settings import api_settings
# from django.db.models import Q
# from profiles.serializers import ClientProfileGetSerializer, ClientProfileUpdateSerializer, UserChangePasswordSerializer, \
#     FormUserAnswerCreatePostSerializer, ClientProfileMerchantSerializer, ApplicationBaseSerializer, \
#     ApplicationClientConfirmedSerializer, ApplicationClientFinishedSerializer, ApplicationDeclinedSerializer, \
#     ApplicationMerchantConfirmedDeclinedWaitingSerializer, ApplicationDeclineSerializer, ApplicationDetailSerializer, \
#     ApplicationCreateSerializer, MerchantProfileTopSerializer, MerchantProfileGetSerializer, MerchantProfileForUpdate, \
#     MerchantProfileUpdate, PaidFeatureTypeListSerializer, GetStatiscticsInSerialzier, GetStatiscticsOutSerialzier
# from users.serializers import PhoneSerializer, ClientRatingCreateSerializer, MerchantReviewCreateSerializer, \
#     MerchantReviewDetailList, MerchantReviewReplyCreateSerializer
# from users.models import MainUser, MerchantPhone, MerchantReview, ReviewReply
# from profiles.models import FormQuestionGroup, Application, ApplicationDocument, PaidFeatureType, Transaction, \
#     UsersPaidFeature, ProjectPaidFeature, Notification
# from profiles.serializers import FormQuestionGroupSerializer, ProjectForPromotionSerialzier, NotificationSerializer
# from main.models import Project, ProjectType, ProjectStyle, ProjectPurpose, ProjectCategory, ProjectView, ProjectComment, \
#     ProjectCommentReply
# from main.serializers import ProjectProfileGetSerializer, ProjectCreateSerializer, ProjectDetailSerializer, \
#     ProjectUpdateSerializer, ProjectPromotionSerializer, ProjectForUpdateSerializer, ProjectCategoryShortSerializer, \
#     ProjectPurposeShortSerializer, ProjectTypeSerializer, ProjectStyleSerializer, \
#     ProjectCategorySpecializationSerializer, ProjectSearchSerializer, ProjectShortSerializer, \
#     ProjectCommentReplyCreateSerializer
# from main.tasks import deactivate_user_feature, deactivate_project_feature, notify_user_feature, notify_project_feature
# from utils import response, pagination
# from utils.permissions import IsClient, IsAuthenticated, IsMerchant, HasPhone
# from datetime import timedelta, datetime
# from dateutil.relativedelta import relativedelta
# import constants
#
# jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
# jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#
#
# class ProfileViewSet(viewsets.GenericViewSet,
#                      mixins.UpdateModelMixin):
#     queryset = MainUser.objects.all()
#     permission_classes = (permissions.IsAuthenticated, )
#
#     @action(detail=False, methods=['get', 'put'], permission_classes=[permissions.IsAuthenticated])
#     def my_profile(self, request, pk=None):
#         request.data._mutable = True
#         user = request.user
#         if request.method == 'GET':
#             if user.role == constants.ROLE_CLIENT:
#                 serializer = ClientProfileGetSerializer(user, context=request)
#                 return Response(serializer.data)
#             elif user.role == constants.ROLE_MERCHANT:
#                 serializer = MerchantProfileGetSerializer(user, context=request)
#                 return Response(serializer.data)
#         if request.method == 'PUT':
#             if user.role == constants.ROLE_CLIENT:
#                 profile = user.profile
#                 email = request.data.get('email')
#                 if email:
#                     user_data = {
#                         'email': email
#                     }
#                 else:
#                     user_data = None
#                 phone = request.data.get('phone')
#                 context = {
#                     'phone': phone,
#                     'user_data': user_data
#                 }
#                 serializer = ClientProfileUpdateSerializer(profile, data=request.data, context=context)
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response(serializer.data, status.HTTP_200_OK)
#                 return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#             elif user.role == constants.ROLE_MERCHANT:
#                 phones = []
#                 if request.data.get('phones'):
#                     phones = request.data.pop('phones')
#                 documents = []
#                 if request.data.get('documents'):
#                     documents = request.data.pop('documents')
#                 delete_documents = []
#                 if request.data.get('delete_documents'):
#                     delete_documents = request.data.pop('delete_documents')
#                 total_documents = request.data.get('total_documents')
#                 if total_documents:
#                     try:
#                         if int(total_documents) > 6:
#                             return Response(response.make_messages([f'{constants.RESPONSE_MAX_FILES} 6']),
#                                             status.HTTP_400_BAD_REQUEST)
#                     except:
#                         return Response(
#                             response.make_messages([f'total_documents: {constants.RESPONSE_RIGHT_ONLY_DIGITS}']),
#                             status.HTTP_400_BAD_REQUEST
#                         )
#                 else:
#                     return Response(response.make_messages([f'total_documents: {constants.RESPONSE_FIELD_REQUIRED}']),
#                                     status.HTTP_400_BAD_REQUEST)
#                 context = {
#                     'phones': phones,
#                     'documents': documents,
#                     'delete_documents': delete_documents,
#                     'email': request.data.get('email')
#                 }
#                 profile = request.user.profile
#                 serializer = MerchantProfileUpdate(profile, data=request.data, context=context)
#                 if serializer.is_valid():
#                     serializer.save()
#                     payload = jwt_payload_handler(user)
#                     token = jwt_encode_handler(payload)
#                     data = {
#                         'token': token
#                     }
#                     return Response(data)
#                 return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=False, methods=['put'], permission_classes=[permissions.IsAuthenticated])
#     def change_password(self, request, pk=None):
#         user = request.user
#         serializer = UserChangePasswordSerializer(user, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status.HTTP_200_OK)
#         return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=False, methods=['get', 'post'], permission_classes=[IsClient])
#     def client_form(self, request, pk=None):
#         if request.method == 'GET':
#             groups = FormQuestionGroup.objects.all().order_by('position')
#             serializer = FormQuestionGroupSerializer(groups, many=True)
#             return Response(serializer.data)
#         elif request.method == 'POST':
#             serializer = FormUserAnswerCreatePostSerializer(data=request.data, context=request)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(status=status.HTTP_200_OK)
#             return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
#     def client(self, request, pk=None):
#         try:
#             user = MainUser.objects.get(id=pk)
#         except MainUser.DoesNotExist:
#             return Response(response.make_messages([f'Пользователь {pk} {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         if user.role == constants.ROLE_MERCHANT:
#             return Response(response.make_messages([constants.RESPONSE_USER_NOT_CLIENT]), status.HTTP_400_BAD_REQUEST)
#         serializer = ClientProfileMerchantSerializer(user, context=request)
#         return Response(serializer.data)
#
#     @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
#     def top_info(self, request, pk=None):
#         user = request.user
#         serializer = MerchantProfileTopSerializer(user, context=request)
#         return Response(serializer.data, status.HTTP_200_OK)
#
#     @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
#     def for_update(self, request, pk=None):
#         serializer = MerchantProfileForUpdate(request.user.profile, context=request)
#         categories = ProjectCategory.objects.all()
#         categories_serializer = ProjectCategorySpecializationSerializer(categories, many=True)
#         data = {
#             'profile': serializer.data,
#             'categories': categories_serializer.data
#         }
#         return Response(data)
#
#     @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated, IsMerchant])
#     def features(self, request, pk=None):
#         type = request.data.get('type')
#         if not type:
#             return Response(response.make_messages([f'type {constants.RESPONSE_FIELD_REQUIRED}']))
#         if request.method == 'GET':
#             if not isinstance(type, int) or type < 1 or type > len(constants.PAID_FEATURE_TYPES):
#                 return Response(response.make_messages([f'Тип {constants.RESPONSE_PAID_TYPE_INVALID}']))
#             features = PaidFeatureType.objects.filter(type=type)
#             serializer = PaidFeatureTypeListSerializer(features, many=True)
#             return Response(serializer.data)
#         elif request.method == 'POST':
#             try:
#                 type = PaidFeatureType.objects.get(id=type)
#             except:
#                 return Response(response.make_messages([f'Типа {constants.RESPONSE_DOES_NOT_EXIST}']),
#                                 status.HTTP_400_BAD_REQUEST)
#             if type.type == constants.PAID_FEATURE_PRO:
#                 features = UsersPaidFeature.objects.filter(user=request.user, is_active=True)
#                 if features.count() > 0:
#                     feature = features.first()
#                     unit = feature.type.time_unit
#                     amount = feature.type.time_amount
#                     if unit == constants.TIME_DAY:
#                         delta = timedelta(days=amount)
#                     elif unit == constants.TIME_MONTH:
#                         delta = relativedelta(months=+amount)
#                     elif unit == constants.TIME_YEAR:
#                         delta = relativedelta(years=+amount)
#                     else:
#                         delta = timedelta(seconds=10)
#                     feature.expires_at = feature.expires_at + delta
#                     feature.refreshed += 1
#                     feature.save()
#                     notify_user_feature.apply_async(args=[feature.id], eta=(feature.expires_at - timedelta(days=1)))
#                     deactivate_user_feature.apply_async(args=[feature.id], eta=feature.expires_at)
#                     return Response(status=status.HTTP_200_OK)
#                 else:
#                     transaction = Transaction.objects.create(number='test')
#                     UsersPaidFeature.objects.create(user=request.user, type=type, transaction=transaction, is_active=True)
#                 return Response(status=status.HTTP_200_OK)
#             return Response(response.make_messages([f'{constants.RESPONSE_FEATURE_TYPES} Про']))
#
#     @action(detail=False, methods=['get', 'post'], permission_classes=[IsAuthenticated, IsMerchant])
#     def projects(self, request, pk=None):
#         if request.method == 'GET':
#             projects = Project.objects.filter(user=request.user)
#             serializer = ProjectProfileGetSerializer(projects, many=True, context=request)
#             return Response(serializer.data)
#         elif request.method == 'POST':
#             context = {
#                 'render': request.data.get('render')
#             }
#             if request.data.get('documents'):
#                 context['documents'] = request.data.pop('documents')
#                 if context['documents'] > 12:
#                     return Response(response.make_messages([f'{constants.RESPONSE_MAX_FILES} 12']))
#             serializer = ProjectCreateSerializer(data=request.data, context=context)
#             if serializer.is_valid():
#                 serializer.save(user=request.user)
#                 return Response(serializer.data)
#             return Response(response.make_errors(serializer), status=status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['get', 'put', 'delete'], permission_classes=[IsAuthenticated, IsMerchant])
#     def project(self, request, pk=None):
#         try:
#             project = Project.objects.get(id=pk)
#         except:
#             return Response(response.make_messages([f'Проект {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         if project.user != request.user:
#             return Response(response.make_messages([f'{constants.RESPONSE_NOT_OWNER} проекта']),
#                             status.HTTP_400_BAD_REQUEST)
#         if request.method == 'GET':
#             serializer = ProjectDetailSerializer(project, context=request)
#             return Response(serializer.data)
#         elif request.method == 'PUT':
#             documents = []
#             if request.data.get('documents'):
#                 documents = request.data.pop('documents')
#             delete_documents = []
#             if request.data.get('delete_documents'):
#                 delete_documents = request.data.pop('delete_documents')
#             total_documents = request.data.get('total_documents')
#             if total_documents:
#                 try:
#                     if int(total_documents) > 12:
#                         return Response(response.make_messages([f'{constants.RESPONSE_MAX_FILES} 12']),
#                                         status.HTTP_400_BAD_REQUEST)
#                 except:
#                     return Response(
#                         response.make_messages([f'total_documents: {constants.RESPONSE_RIGHT_ONLY_DIGITS}']),
#                         status.HTTP_400_BAD_REQUEST
#                     )
#             else:
#                 return Response(response.make_messages([f'total_documents: {constants.RESPONSE_FIELD_REQUIRED}']),
#                                 status.HTTP_400_BAD_REQUEST)
#             context = {
#                 'documents': documents,
#                 'delete_documents': delete_documents,
#                 'render': request.data.get('render')
#             }
#             serializer = ProjectUpdateSerializer(project, data=request.data, context=context)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data)
#             return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#         elif request.method == 'DELETE':
#             project.delete()
#             return Response(status=status.HTTP_200_OK)
#
#     @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
#     def project_for_update(self, request, pk=None):
#         try:
#             project = Project.objects.get(id=pk)
#         except:
#             return Response(response.make_messages([f'Проект {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         if project.user != request.user:
#             return Response(response.make_messages([f'{constants.RESPONSE_NOT_OWNER} проекта']),
#                             status.HTTP_400_BAD_REQUEST)
#         project_serializer = ProjectForUpdateSerializer(project, context=request)
#         categories = ProjectCategory.objects.all()
#         category_serialzier = ProjectCategoryShortSerializer(categories, many=True)
#         purposes = ProjectPurpose.objects.all()
#         purpose_serialzier = ProjectPurposeShortSerializer(purposes, many=True)
#         types = ProjectType.objects.all()
#         type_serialzier = ProjectTypeSerializer(types, many=True)
#         styles = ProjectStyle.objects.all()
#         style_serialzier = ProjectStyleSerializer(styles, many=True)
#         data = {
#             'project': project_serializer.data,
#             'categories': category_serialzier.data,
#             'purposes': purpose_serialzier.data,
#             'styles': style_serialzier.data,
#             'types': type_serialzier.data
#         }
#         return Response(data)
#
#     @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
#     def promoted(self, request, pk=None):
#         user = request.user
#         features = ProjectPaidFeature.objects.filter(project__user=user)
#         data = []
#         for feature in features:
#             context = {
#                 'type': feature.type.type,
#                 'request': request
#             }
#             serializer = ProjectPromotionSerializer(feature.project, context=context)
#             data.append(serializer.data)
#         return Response(data)
#
#     @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated, IsMerchant])
#     def project_for_promotion(self, request, pk=None):
#         if pk != 'none':
#             try:
#                 project = Project.objects.get(id=pk)
#             except:
#                 return Response(response.make_messages([f'Проект {constants.RESPONSE_DOES_NOT_EXIST}']),
#                                 status.HTTP_400_BAD_REQUEST)
#         else:
#             projects = Project.objects.filter(user=request.user)
#             if projects.count() > 0:
#                 project = projects.first()
#             else:
#                 return Response(constants.RESPONSE_NO_PROJECTS, status.HTTP_400_BAD_REQUEST)
#         if project.user != request.user:
#             return Response(response.make_messages([f'{constants.RESPONSE_NOT_OWNER} проекта']),
#                             status.HTTP_400_BAD_REQUEST)
#         if request.method == 'GET':
#             project_serializer = ProjectSearchSerializer(project, context=request)
#             projects = Project.objects.filter(user=request.user)
#             projects_serializer = ProjectShortSerializer(projects, many=True)
#             data = {
#                 'current_project': project_serializer.data,
#                 'projects': projects_serializer.data
#             }
#             return Response(data)
#         elif request.method == 'POST':
#             serializer = ProjectForPromotionSerialzier(data=request.data)
#             if serializer.is_valid():
#                 type = PaidFeatureType.objects.get(id=serializer.data.get('type'))
#                 if type.type != constants.PAID_FEATURE_TOP_DETAILED:
#                     features = ProjectPaidFeature.objects.filter(project=project, is_active=True,
#                                                                  type__type=type.type)
#                     if features.count() > 0:
#                         feature = features.first()
#                         unit = feature.type.time_unit
#                         amount = feature.type.time_amount
#                         if unit == constants.TIME_DAY:
#                             delta = timedelta(days=amount)
#                         elif unit == constants.TIME_MONTH:
#                             delta = relativedelta(months=+amount)
#                         elif unit == constants.TIME_YEAR:
#                             delta = relativedelta(years=+amount)
#                         else:
#                             delta = timedelta(seconds=10)
#                         feature.expires_at = feature.expires_at + delta
#                         feature.refresh_count += 1
#                         feature.save()
#                         notify_project_feature.apply_async(args=[feature.id],
#                                                         eta=(feature.expires_at - timedelta(days=1)))
#                         deactivate_project_feature.apply_async(args=[feature.id], eta=feature.expires_at)
#                         return Response(status=status.HTTP_200_OK)
#                     transaction = Transaction.objects.create(number='test')
#                     ProjectPaidFeature.objects.create(project=project, type_id=serializer.data.get('type'),
#                                                       transaction=transaction,
#                                                       is_active=True)
#                     return Response(status=status.HTTP_200_OK)
#                 top_type = PaidFeatureType.objects.filter(type=constants.PAID_FEATURE_TOP, position=type.position).first()
#                 if top_type:
#                     features = ProjectPaidFeature.objects.filter(project=project, is_active=True,
#                                                                  type__type=top_type.type)
#                     if features.count() > 0:
#                         feature = features.first()
#                         unit = feature.type.time_unit
#                         amount = feature.type.time_amount
#                         if unit == constants.TIME_DAY:
#                             delta = timedelta(days=amount)
#                         elif unit == constants.TIME_MONTH:
#                             delta = relativedelta(months=+amount)
#                         elif unit == constants.TIME_YEAR:
#                             delta = relativedelta(years=+amount)
#                         else:
#                             delta = timedelta(seconds=10)
#                         feature.expires_at = feature.expires_at + delta
#                         feature.refresh_count += 1
#                         feature.save()
#                         notify_project_feature.apply_async(args=[feature.id],
#                                                            eta=(feature.expires_at - timedelta(days=1)))
#                         deactivate_project_feature.apply_async(args=[feature.id], eta=feature.expires_at)
#                     else:
#                         transaction = Transaction.objects.create(number='test')
#                         ProjectPaidFeature.objects.create(project=project, type=top_type,
#                                                           transaction=transaction,
#                                                           is_active=True)
#                 detailed_type = PaidFeatureType.objects.filter(type=constants.PAID_FEATURE_DETAILED,
#                                                                position=type.position).first()
#                 if detailed_type:
#                     features = ProjectPaidFeature.objects.filter(project=project, is_active=True,
#                                                                  type__type=detailed_type.type)
#                     if features.count() > 0:
#                         feature = features.first()
#                         unit = feature.type.time_unit
#                         amount = feature.type.time_amount
#                         if unit == constants.TIME_DAY:
#                             delta = timedelta(days=amount)
#                         elif unit == constants.TIME_MONTH:
#                             delta = relativedelta(months=+amount)
#                         elif unit == constants.TIME_YEAR:
#                             delta = relativedelta(years=+amount)
#                         else:
#                             delta = timedelta(seconds=10)
#                         feature.expires_at = feature.expires_at + delta
#                         feature.refresh_count += 1
#                         feature.save()
#                         notify_project_feature.apply_async(args=[feature.id],
#                                                            eta=(feature.expires_at - timedelta(days=1)))
#                         deactivate_project_feature.apply_async(args=[feature.id], eta=feature.expires_at)
#                         return Response(status=status.HTTP_200_OK)
#                     else:
#                         transaction = Transaction.objects.create(number='test')
#                         ProjectPaidFeature.objects.create(project=project, type=detailed_type,
#                                                           transaction=transaction,
#                                                           is_active=True)
#                     return Response(status=status.HTTP_200_OK)
#                 return Response(status=status.HTTP_200_OK)
#             return Response(response.make_errors(serializer), status=status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['get', 'post'], permission_classes=[IsAuthenticated, IsMerchant])
#     def statistics(self, request, pk=None):
#         try:
#             feature = ProjectPaidFeature.objects.get(id=pk)
#         except:
#             return Response(response.make_messages([f'Прдвиженияе прооекта {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         if feature.project.user != request.user:
#             return Response(response.make_messages([f'{constants.RESPONSE_NOT_OWNER} продвижением проекта']),
#                             status.HTTP_400_BAD_REQUEST)
#         serializer = GetStatiscticsInSerialzier(data=request.data)
#         if serializer.is_valid():
#             type = serializer.data.get('type')
#             time_period = serializer.data.get('time_period')
#             if time_period == constants.STATISTICS_TIME_7_DAYS:
#                 days = 7
#             elif time_period == constants.STATISTICS_TIME_30_DAYS:
#                 days = 30
#             today = datetime.today()
#             statistics_data = []
#             for day in range(days):
#                 with_delta = today - timedelta(days=day)
#                 if type == constants.STATISTICS_TYPE_VIEWS:
#                     statistics_data.append({
#                         "date": with_delta.strftime(constants.DATE_FORMAT),
#                         "count": ProjectView.objects.filter(project=feature.project, creation_date__day=with_delta.day,
#                                                             creation_date__month=with_delta.month).count()
#                     })
#                 if type == constants.STATISTICS_TYPE_APPS:
#                     statistics_data.append({
#                         "date": with_delta.strftime(constants.DATE_FORMAT),
#                         "count": Application.objects.filter(project=feature.project,
#                                                             creation_date__day=with_delta.day,
#                                                             creation_date__month=with_delta.month).count()
#                     })
#             project_serializer = GetStatiscticsOutSerialzier(feature)
#             data = {
#                 'project_data': project_serializer.data,
#                 'statistics_data': statistics_data
#             }
#             return Response(data, status.HTTP_200_OK)
#         return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, IsMerchant])
#     def get_reviews(self, request, pk=None):
#         user = request.user
#         if user.role == constants.ROLE_CLIENT:
#             return Response(response.make_messages([constants.RESPONSE_USER_NOT_MERCHANT]))
#         reviews = MerchantReview.objects.filter(merchant=user)
#         if request.data.get('order_by'):
#             order_by = request.data.get('order_by')
#         else:
#             order_by = '-creation_date'
#         reviews = reviews.order_by(order_by)
#         paginator = pagination.CustomPagination()
#         paginator.page_size = 8
#         page = paginator.paginate_queryset(reviews, request)
#         if page is not None:
#             serializer = MerchantReviewDetailList(reviews, many=True, context=request)
#             data = {
#                 'total_found': reviews.count()
#             }
#             return paginator.get_paginated_response(serializer.data, additional_data=data)
#         serializer = MerchantReviewDetailList(reviews, many=True, context=request)
#         return Response(serializer.data, status.HTTP_200_OK)
#
#     @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
#     def delete_review(self, request, pk=None):
#         try:
#             review = MerchantReview.objects.get(id=pk)
#         except:
#             return Response(response.make_messages([f'Отзыв {pk} {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         user = request.user
#         if review.merchant != user:
#             return Response(constants.RESPONSE_NOT_OWNER, status.HTTP_400_BAD_REQUEST)
#         review.delete()
#         return Response(status=status.HTTP_200_OK)
#
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMerchant])
#     def review_reply(self, request, pk=None):
#         try:
#             review = MerchantReview.objects.get(id=pk)
#         except:
#             return Response(response.make_messages([f'Отзыв {pk} {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         try:
#             ReviewReply.objects.get(review=review)
#             return Response(response.make_messages([constants.RESPONSE_REPLY_EXISTS]))
#         except:
#             pass
#         user = request.user
#         if review.merchant != user:
#             return Response(constants.RESPONSE_NOT_OWNER, status.HTTP_400_BAD_REQUEST)
#         context = {
#             'user': user
#         }
#         if request.data.get('documents'):
#             documents = request.data.pop('documents')
#             context['documents'] = documents
#         serialzier = MerchantReviewReplyCreateSerializer(data=request.data, context=context)
#         if serialzier.is_valid():
#             serialzier.save(review=review, user=user)
#             return Response(serialzier.data, status.HTTP_200_OK)
#         return Response(response.make_errors(serialzier), status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
#     def delete_review_reply(self, request, pk=None):
#         try:
#             reply = ReviewReply.objects.get(id=pk)
#         except:
#             return Response(response.make_messages([f'Ответ на отзыв {pk} {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         user = request.user
#         if reply.user != user:
#             return Response(constants.RESPONSE_NOT_OWNER, status.HTTP_400_BAD_REQUEST)
#         reply.delete()
#         return Response(status=status.HTTP_200_OK)
#
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMerchant])
#     def comment_reply(self, request, pk=None):
#         try:
#             comment = ProjectComment.objects.get(id=pk)
#         except Project.DoesNotExist:
#             return Response(response.make_messages([f'Комментарий {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         if comment.project.user != request.user:
#             return Response(response.make_messages([constants.RESPONSE_NOT_OWNER]))
#         try:
#             ProjectCommentReply.objects.get(comment=comment)
#             return Response(response.make_messages([constants.RESPONSE_COMMENT_REPLY_EXISTS]))
#         except:
#             pass
#         context = {}
#         if request.data.get('documents'):
#             documents = request.data.pop('documents')
#             context['documents'] = documents
#         serializer = ProjectCommentReplyCreateSerializer(data=request.data, context=context)
#         if serializer.is_valid():
#             serializer.save(comment=comment, user=request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(response.make_errors(serializer), status=status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
#     def delete_comment(self, request, pk=None):
#         try:
#             comment = ProjectComment.objects.get(id=pk)
#         except Project.DoesNotExist:
#             return Response(response.make_messages([f'Комментарий {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         if comment.project.user != request.user:
#             return Response(response.make_messages([constants.RESPONSE_NOT_OWNER]))
#         comment.delete()
#         return Response(status=status.HTTP_200_OK)
#
#     @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated, IsMerchant])
#     def delete_comment_reply(self, request, pk=None):
#         try:
#             reply = ProjectCommentReply.objects.get(id=pk)
#         except Project.DoesNotExist:
#             return Response(response.make_messages([f'Комментарий {constants.RESPONSE_DOES_NOT_EXIST}']),
#                             status.HTTP_400_BAD_REQUEST)
#         if reply.user != request.user:
#             return Response(response.make_messages([constants.RESPONSE_NOT_OWNER]))
#         reply.delete()
#         return Response(status=status.HTTP_200_OK)
#
#     @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
#     def notifications(self, request, pk=None):
#         user = request.user
#         notifications = Notification.objects.filter(user=user)
#         paginator = pagination.CustomPagination()
#         paginator.page_size = 13
#         page = paginator.paginate_queryset(notifications, request)
#         if page is not None:
#             serializer = NotificationSerializer(notifications, many=True)
#             return paginator.get_paginated_response(serializer.data)
#         serializer = NotificationSerializer(notifications, many=True)
#         return Response(serializer.data, status.HTTP_200_OK)
#
#     @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
#     def read_notification(self, request, pk=None):
#         try:
#             notification = Notification.objects.get(id=pk)
#         except:
#             return Response(response.make_messages([f'Уведомление {constants.RESPONSE_DOES_NOT_EXIST}']))
#         if notification.user != request.user:
#             return Response(response.make_messages([constants.RESPONSE_NOT_OWNER]))
#         notification.read = True
#         notification.save()
#         return Response(status=status.HTTP_200_OK)
#
#
# class IsPhoneValidView(views.APIView):
#     permission_classes = [permissions.IsAuthenticated, ]
#     http_method_names = ['post']
#     parser_classes = (FormParser, MultiPartParser, JSONParser,)
#
#     def post(self, request, format=None):
#         phone = request.data.get('phone')
#         serializer = PhoneSerializer(data={
#             'phone': phone
#         })
#         if serializer.is_valid():
#             is_valid = False
#             try:
#                 phone_obj = MerchantPhone.objects.get(phone=phone)
#                 is_valid = phone_obj.is_valid
#             except:
#                 pass
#             if phone_obj:
#                 if phone_obj.user:
#                     if phone_obj.user != request.user:
#                         return Response(response.make_messages([constants.RESPONSE_PHONE_REGISTERED]))
#             data = {
#                 'is_valid': is_valid
#             }
#             return Response(data)
#         return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#
#
# class ApplicationViewSet(viewsets.GenericViewSet,
#                          mixins.ListModelMixin,
#                          mixins.RetrieveModelMixin,
#                          mixins.CreateModelMixin):
#     queryset = Application.objects.all()
#     permission_classes = [IsAuthenticated, ]
#
#     def list(self, request, *args, **kwargs):
#         status_name = request.GET.get('status') if request.GET.get('status') else constants.APPLICATION_CREATED_STRING
#         user = request.user
#
#         if status_name not in constants.APPLICATION_STATUSES_STRING:
#             return Response(response.make_messages([constants.RESPONSE_STATUS_NOT_VALID]), status.HTTP_400_BAD_REQUEST)
#
#         if status_name == constants.APPLICATION_CREATED_STRING:
#             queryset = self.get_queryset().filter(status=constants.APPLICATION_CREATED)
#             serializer_class = ApplicationBaseSerializer
#         elif status_name == constants.APPLICATION_CONFIRMED_STRING:
#             queryset = self.get_queryset().filter(status=constants.APPLICATION_CONFIRMED)
#             if user.role == constants.ROLE_CLIENT:
#                 serializer_class = ApplicationClientConfirmedSerializer
#             elif user.role == constants.ROLE_MERCHANT:
#                 serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
#         elif status_name == constants.APPLICATION_FINISHED_STRING:
#             queryset = self.get_queryset().filter(status=constants.APPLICATION_FINISHED)
#             if user.role == constants.ROLE_CLIENT:
#                 serializer_class = ApplicationBaseSerializer
#             elif user.role == constants.ROLE_MERCHANT:
#                 serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
#         elif status_name == constants.APPLICATION_FINISHED_CONFIRMED_STRING:
#             queryset = self.get_queryset().filter(status=constants.APPLICATION_FINISHED_CONFIRMED)
#             if user.role == constants.ROLE_CLIENT:
#                 serializer_class = ApplicationClientFinishedSerializer
#             elif user.role == constants.ROLE_MERCHANT:
#                 serializer_class = ApplicationMerchantConfirmedDeclinedWaitingSerializer
#         elif status_name == constants.APPLICATION_DECLINED_STRING:
#             queryset = self.get_queryset().filter(Q(status=constants.APPLICATION_DECLINED_CLIENT) |
#                                                   Q(status=constants.APPLICATION_DECLINED_MERCHANT))
#             serializer_class = ApplicationDeclinedSerializer
#
#         paginator = pagination.CustomPagination()
#         paginator.page_size = 2
#         page = paginator.paginate_queryset(queryset, request=request)
#
#         if page is not None:
#             serializer = serializer_class(page, many=True, context=request)
#             return paginator.get_paginated_response(serializer.data)
#
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)
#
#     def retrieve(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = ApplicationDetailSerializer(instance, context=request)
#         return Response(serializer.data)
#
#     @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
#     def finish(self, request, pk=None):
#         try:
#             application = Application.objects.get(id=pk)
#         except Application.DoesNotExist:
#             return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
#         user = request.user
#         if user.role == constants.ROLE_CLIENT:
#             if application.client != user:
#                 return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
#             if application.status != constants.APPLICATION_CONFIRMED:
#                 return Response(response.make_messages([f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Приянятые']),
#                                 status.HTTP_400_BAD_REQUEST)
#             context = {
#                 'user': user
#             }
#             if request.data.get('documents'):
#                 documents = request.data.pop('documents')
#                 context['documents'] = documents
#             serialzier = MerchantReviewCreateSerializer(data=request.data, context=context)
#             if serialzier.is_valid():
#                 serialzier.save(merchant=application.merchant, user=user)
#                 application.status = constants.APPLICATION_FINISHED
#                 application.save()
#                 return Response(serialzier.data, status.HTTP_200_OK)
#             return Response(response.make_errors(serialzier), status.HTTP_400_BAD_REQUEST)
#         elif user.role == constants.ROLE_MERCHANT:
#             if application.merchant != user:
#                 return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
#             if application.status != constants.APPLICATION_CONFIRMED and \
#                     application.status != constants.APPLICATION_FINISHED:
#                 return Response(
#                     response.make_messages(
#                         [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают подтверждения, в процессе']
#                     ),
#                     status.HTTP_400_BAD_REQUEST
#                 )
#             serializer = ClientRatingCreateSerializer(data=request.data)
#             if serializer.is_valid():
#                 serializer.save(user=user, client=application.client)
#                 application.status = constants.APPLICATION_FINISHED_CONFIRMED
#                 application.save()
#                 return Response(serializer.data, status.HTTP_200_OK)
#             return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
#     def decline(self, request, pk=None):
#         try:
#             application = Application.objects.get(id=pk)
#         except Application.DoesNotExist:
#             return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
#         user = request.user
#         if user.role == constants.ROLE_CLIENT:
#             if application.client != user:
#                 return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
#             if application.status != constants.APPLICATION_CREATED:
#                 return Response(response.make_messages([f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Ожидают ответа']),
#                                 status.HTTP_400_BAD_REQUEST)
#             application.status = constants.APPLICATION_DECLINED_CLIENT
#             application.save()
#             return Response(status=status.HTTP_200_OK)
#         elif user.role == constants.ROLE_MERCHANT:
#             if application.merchant != user:
#                 return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
#             if application.status != constants.APPLICATION_CREATED:
#                 return Response(
#                     response.make_messages(
#                         [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые']
#                     ),
#                     status.HTTP_400_BAD_REQUEST
#                 )
#             serializer = ApplicationDeclineSerializer(application, data=request.data)
#             if serializer.is_valid():
#                 serializer.save()
#                 return Response(serializer.data, status.HTTP_200_OK)
#             return Response(response.make_errors(serializer), status.HTTP_400_BAD_REQUEST)
#
#     @action(detail=True, methods=['post'], permission_classes=[IsMerchant])
#     def accept(self, request, pk=None):
#         try:
#             application = Application.objects.get(id=pk)
#         except Application.DoesNotExist:
#             return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
#         user = request.user
#         if application.merchant != user:
#             return Response(response.make_messages([constants.RESPONSE_CANT_MODIFY]))
#         if application.status != constants.APPLICATION_CREATED:
#             return Response(
#                 response.make_messages(
#                     [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Новые']
#                 ),
#                 status.HTTP_400_BAD_REQUEST
#             )
#         application.status = constants.APPLICATION_CONFIRMED
#         application.save()
#         return Response(status.HTTP_200_OK)
#
#     @action(detail=True, methods=['post'], permission_classes=[IsClient, HasPhone])
#     def resend(self, request, pk=None):
#         try:
#             application = Application.objects.get(id=pk)
#         except Application.DoesNotExist:
#             return Response(response.make_messages([f'Заявка с id {pk} {constants.RESPONSE_DOES_NOT_EXIST}']))
#         if application.status != constants.APPLICATION_FINISHED_CONFIRMED:
#             return Response(
#                 response.make_messages(
#                     [f'{constants.RESPONSE_APPLICATION_STATUS_NOT_VALID} Завершенные']
#                 ),
#                 status.HTTP_400_BAD_REQUEST
#             )
#         context = {
#         }
#         if request.data.get('documents'):
#             documents = request.data.pop('documents')
#             context['documents'] = documents
#         serializer = ApplicationCreateSerializer(data=request.data, context=context)
#         if serializer.is_valid():
#             serializer.save(client=application.client, merchant=application.merchant, project=application.project)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(response.make_errors(serializer), status=status.HTTP_400_BAD_REQUEST)
