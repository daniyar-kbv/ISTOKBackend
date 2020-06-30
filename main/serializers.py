from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser
from main.models import Project, ProjectDocument, ProjectUserFavorite, ProjectComment, ProjectView, ProjectCommentReply, \
    ProjectCommentDocument, Render360, ProjectType, ProjectCommentReplyDocument
from users.models import ProjectCategory, ProjectType, ProjectStyle, ProjectPurpose, ProjectPurposeSubType, ProjectTag, \
    ProjectPurposeType, MerchantProfile, Specialization
from users.models import Country, City
from users.serializers import UserShortSerializer, UserMediumSerializer, UserShortAvatarSerializer, \
    SpecializationSerializer
from profiles.models import ProjectPaidFeature, Application
from utils import response, upload
import constants, math


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ('id', 'name')


class CountrySerializer(serializers.ModelSerializer):
    cities = serializers.SerializerMethodField()

    class Meta:
        model = Country
        fields = ('id', 'name', 'cities')

    def get_cities(self, obj):
        cities = City.objects.filter(country=obj)
        serializer = CitySerializer(cities, many=True)
        return serializer.data


class ProjectCategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ('id', 'name')


class ProjectCategorySpecializationSerializer(serializers.ModelSerializer):
    specializations = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCategory
        fields = ('id', 'name', 'specializations')

    def get_specializations(self, obj):
        specializations = Specialization.objects.filter(category=obj)
        serializer = SpecializationSerializer(specializations, many=True)
        return serializer.data


class ProjectCategorySerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCategory
        fields = ('name', 'description', 'photo')

    def get_photo(self, obj):
        if obj.image:
            return self.context.build_absolute_uri(obj.image.url)
        return None


class ProjectPurposeSubtypeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPurposeSubType
        fields = ('id', 'name')


class ProjectPurposeSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPurposeSubType
        fields = '__all__'


class ProjectPurposeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPurposeType
        fields = '__all__'


class ProjectPurposeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPurpose
        fields = ('id', 'name')


class ProjectPurposeSerializer(serializers.ModelSerializer):
    type = ProjectPurposeTypeSerializer()
    subtype = ProjectPurposeSubtypeSerializer()

    class Meta:
        model = ProjectPurpose
        fields = '__all__'


class ProjectPurposeWithTypeSerializer(serializers.ModelSerializer):
    subtype = ProjectPurposeSubtypeShortSerializer()

    class Meta:
        model = ProjectPurpose
        fields = ('id', 'name', 'subtype')


class ProjectPurposeTypeFullSerializer(serializers.ModelSerializer):
    purposes = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPurposeType
        fields = ('id', 'name', 'purposes')

    def get_purposes(self, obj):
        purposes = ProjectPurpose.objects.filter(type=obj)
        serializer = ProjectPurposeWithTypeSerializer(purposes, many=True)
        return serializer.data


class ProjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = '__all__'


class ProjectStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStyle
        fields = '__all__'


class ProjectTagShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ('id', 'name')


class ProjectTagSerializer(serializers.ModelSerializer):
    category = ProjectCategorySerializer()

    class Meta:
        model = ProjectTag
        fields = '__all__'


class ProjectMainPageSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    is_favorite = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    price_from_full = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'user', 'name', 'price_from_full', 'rating', 'is_favorite', 'is_top', 'photo')

    def get_user_id(self, obj):
        return obj.user.id

    def get_user_name(self, obj):
        return f'{obj.user.get_full_name()}'

    def get_is_favorite(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if ProjectUserFavorite.objects.filter(user=self.context.user, project=obj).count() > 0:
                return True
            else:
                return False
        return None

    def get_photo(self, obj):
        photo = ProjectDocument.objects.filter(project=obj).first()
        if photo:
            return self.context.build_absolute_uri(photo.document.url)
        return None

    def get_price_from_full(self, obj):
        price = int(obj.price_from) if obj.price_from % math.trunc(obj.price_from) == 0 else obj.price_from
        return f'от {price} тг/м2'


class ProjectModalSerializer(serializers.ModelSerializer):
    city_name = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    purpose_name = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    style_name = serializers.SerializerMethodField()
    area_full = serializers.SerializerMethodField()
    price_from_full = serializers.SerializerMethodField()
    price_total_full = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'city_name', 'category_name', 'purpose_name', 'type_name', 'style_name', 'area_full',
                  'price_from_full', 'price_total_full', 'is_favorite', 'photos')

    def get_city_name(self, obj):
        try:
            return obj.user.merchant_profile.city.name
        except:
            return None

    def get_category_name(self, obj):
        return obj.category.name

    def get_purpose_name(self, obj):
        return f'{obj.purpose.type.name} - {obj.purpose.subtype.name} - {obj.purpose.name}'

    def get_type_name(self, obj):
        return obj.type.name

    def get_style_name(self, obj):
        return obj.style.name

    def get_area_full(self, obj):
        area = int(obj.area) if obj.area % math.trunc(obj.area) == 0 else obj.area
        return f'{area} м2'

    def get_price_from_full(self, obj):
        price = int(obj.price_from) if obj.price_from % math.trunc(obj.price_from) == 0 else obj.price_from
        return f'от {price} тг/м2'

    def get_price_total_full(self, obj):
        price_from = int(obj.price_from) if obj.price_from % math.trunc(obj.price_from) == 0 else obj.price_from
        price_to = int(obj.price_to) if obj.price_to % math.trunc(obj.price_to) == 0 else obj.price_to
        return f'от {price_from} - {price_to} тг/м2'

    def get_is_favorite(self, obj):
        try:
            ProjectUserFavorite.objects.get(user=self.context.user, project=obj)
            return True
        except:
            return False

    def get_photos(self, obj):
        urls = []
        project_documents = ProjectDocument.objects.filter(project=obj)
        for doc in project_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls


class ServicesMainPageSerialzier(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    merchants_count = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCategory
        fields = ('id', 'name', 'description', 'photo', 'merchants_count')

    def get_photo(self, obj):
        if obj.image:
            return self.context.build_absolute_uri(obj.image.url)
        return None

    def get_merchants_count(self, obj):
        return MerchantProfile.objects.filter(categories__in=[obj]).count()


class ProjectDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectDocument
        fields = '__all__'


class Render360Serializer(serializers.ModelSerializer):
    class Meta:
        model = Render360
        fields = '__all__'


class Render360CreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Render360
        fields = ('document', )


class ProjectShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name')


class ProjectSearchSerializer(serializers.ModelSerializer):
    user = UserShortAvatarSerializer()
    is_favorite = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    price_from_full = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'user', 'name', 'price_from_full', 'rating', 'is_favorite', 'is_top', 'is_detailed',
                  'photo')

    def get_is_favorite(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if ProjectUserFavorite.objects.filter(user=self.context.user, project=obj).count() > 0:
                return True
            else:
                return False
        return None

    def get_photo(self, obj):
        photo = ProjectDocument.objects.filter(project=obj).first()
        if photo:
            return self.context.build_absolute_uri(photo.document.url)
        return None

    def get_price_from_full(self, obj):
        price = int(obj.price_from) if obj.price_from % math.trunc(obj.price_from) == 0 else obj.price_from
        return f'от {price} тг/м2'


class ProjectDetailListSerializer(ProjectSearchSerializer):
    user = UserShortAvatarSerializer()


class ProjectProfileGetSerializer(ProjectSearchSerializer):
    user = UserShortAvatarSerializer()

    class Meta(ProjectSearchSerializer.Meta):
        fields_ = ProjectSearchSerializer.Meta.fields
        fields_ = list(fields_)
        fields_.remove('is_favorite')
        fields_.remove('is_top')
        fields_.remove('is_detailed')
        fields = tuple(fields_)


class ProjectPromotionSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    views_count = serializers.SerializerMethodField()
    applications_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    favorite_count = serializers.SerializerMethodField()
    paid_feature_id = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'name', 'photo', 'start_date', 'end_date', 'views_count', 'applications_count', 'price',
                  'favorite_count', 'rating', 'is_top', 'is_detailed', 'paid_feature_id')

    def get_photo(self, obj):
        photo = ProjectDocument.objects.filter(project=obj).first()
        if photo:
            return self.context.get('request').build_absolute_uri(photo.document.url)
        return None

    def get_start_date(self, obj):
        queryset = ProjectPaidFeature.objects.filter(project=obj, is_active=True)
        if self.context.get('type') == constants.PAID_FEATURE_TOP:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_TOP)
        elif self.context.get('type') == constants.PAID_FEATURE_DETAILED:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_DETAILED)
        feature = queryset.first()
        return feature.created_at.strftime(constants.DATE_FORMAT)

    def get_end_date(self, obj):
        queryset = ProjectPaidFeature.objects.filter(project=obj, is_active=True)
        if self.context.get('type') == constants.PAID_FEATURE_TOP:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_TOP)
        elif self.context.get('type') == constants.PAID_FEATURE_DETAILED:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_DETAILED)
        feature = queryset.first()
        return feature.expires_at.strftime(constants.DATE_FORMAT)

    def get_views_count(self, obj):
        return ProjectView.objects.filter(project=obj).count()

    def get_applications_count(self, obj):
        return Application.objects.filter(project=obj).count()

    def get_price(self, obj):
        queryset = ProjectPaidFeature.objects.filter(project=obj, is_active=True)
        if self.context.get('type') == constants.PAID_FEATURE_TOP:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_TOP)
        elif self.context.get('type') == constants.PAID_FEATURE_DETAILED:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_DETAILED)
        feature = queryset.first()
        return feature.type.price

    def get_favorite_count(self, obj):
        return ProjectUserFavorite.objects.filter(project=obj).count()

    def get_paid_feature_id(self, obj):
        queryset = ProjectPaidFeature.objects.filter(project=obj, is_active=True)
        if self.context.get('type') == constants.PAID_FEATURE_TOP:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_TOP)
        elif self.context.get('type') == constants.PAID_FEATURE_DETAILED:
            queryset = queryset.filter(type__type=constants.PAID_FEATURE_DETAILED)
        feature = queryset.first()
        return feature.id


class ProjectCreateSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(required=True, write_only=True)
    purpose = serializers.IntegerField(required=True, write_only=True)
    style = serializers.IntegerField(required=True, write_only=True)
    type = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = Project
        fields = ('name', 'category', 'purpose', 'type', 'style', 'area', 'price_from', 'price_to', 'description',
                  'tags',)

    def create(self, validated_data):
        try:
            category = ProjectCategory.objects.get(id=validated_data.pop('category'))
        except:
            return serializers.ValidationError(f'Category {constants.RESPONSE_DOES_NOT_EXIST}')
        try:
            purpose = ProjectPurpose.objects.get(id=validated_data.pop('purpose'))
        except:
            return serializers.ValidationError(f'Purpose {constants.RESPONSE_DOES_NOT_EXIST}')
        try:
            style = ProjectStyle.objects.get(id=validated_data.pop('style'))
        except:
            return serializers.ValidationError(f'Style {constants.RESPONSE_DOES_NOT_EXIST}')
        try:
            type = ProjectType.objects.get(id=validated_data.pop('type'))
        except:
            return serializers.ValidationError(f'Type {constants.RESPONSE_DOES_NOT_EXIST}')
        if validated_data.get('price_from') > validated_data.get('price_to'):
            raise serializers.ValidationError(response.make_messages([constants.VALIDATION_PRICE_INVALID]))
        tags = validated_data.pop('tags')
        project = Project.objects.create(**validated_data,
                                         category=category,
                                         purpose=purpose,
                                         style=style,
                                         type=type)
        documents = self.context.get('documents')
        doc_objects = []
        if documents:
            for doc in documents:
                doc_data = {
                    'project': project.id,
                    'document': doc
                }
                serializer = ProjectDocumentSerializer(data=doc_data)
                if serializer.is_valid():
                    doc_objects.append(serializer.save())
                else:
                    project.delete()
                    for doc_obj in doc_objects:
                        doc_obj.delete()
                    raise serializers.ValidationError(response.make_errors(serializer))
        render = self.context.get('render')
        if render:
            doc_data = {
                'project': project.id,
                'document': render
            }
            serializer = Render360CreateSerializer(data=doc_data)
            if serializer.is_valid():
                serializer.save()
            else:
                project.delete()
                for doc_obj in doc_objects:
                    doc_obj.delete()
                raise serializers.ValidationError(response.make_errors(serializer))
        for tag in tags:
            project.tags.add(tag)
        project.save()
        return project


class ProjectUpdateSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(required=False, write_only=True)
    purpose = serializers.IntegerField(required=False, write_only=True)
    style = serializers.IntegerField(required=False, write_only=True)
    type = serializers.IntegerField(required=False, write_only=True)
    area = serializers.FloatField(required=False)
    price_from = serializers.FloatField(required=False)
    price_to = serializers.FloatField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = Project
        fields = ('name', 'category', 'purpose', 'type', 'style', 'area', 'price_from', 'price_to', 'description',
                  'tags',)

    def update(self, instance, validated_data):
        category = None
        if validated_data.get('category'):
            try:
                category = ProjectCategory.objects.get(id=validated_data.pop('category'))
            except:
                raise serializers.ValidationError(f'Category {constants.RESPONSE_DOES_NOT_EXIST}')
        purpose = None
        if validated_data.get('purpose'):
            try:
                purpose = ProjectPurpose.objects.get(id=validated_data.pop('purpose'))
            except:
                raise serializers.ValidationError(f'Purpose {constants.RESPONSE_DOES_NOT_EXIST}')
        style = None
        if validated_data.get('style'):
            try:
                style = ProjectStyle.objects.get(id=validated_data.pop('style'))
            except:
                raise serializers.ValidationError(f'Style {constants.RESPONSE_DOES_NOT_EXIST}')
        type = None
        if validated_data.get('type'):
            try:
                type = ProjectType.objects.get(id=validated_data.pop('type'))
            except:
                raise serializers.ValidationError(f'Type {constants.RESPONSE_DOES_NOT_EXIST}')
        if validated_data.get('price_from') and validated_data.get('price_to'):
            if validated_data.get('price_from') > validated_data.get('price_to'):
                raise serializers.ValidationError(response.make_messages([constants.VALIDATION_PRICE_INVALID]))
        elif validated_data.get('price_from'):
            if validated_data.get('price_from') > instance.price_from:
                raise serializers.ValidationError(response.make_messages([constants.VALIDATION_PRICE_INVALID]))
        elif validated_data.get('price_to'):
            if instance.price_from > validated_data.get('price_to'):
                raise serializers.ValidationError(response.make_messages([constants.VALIDATION_PRICE_INVALID]))
        documents = self.context.get('documents')
        doc_serializers = []
        if documents:
            for document in documents:
                doc_data = {
                    'project': instance.id,
                    'document': document
                }
                serializer = ProjectDocumentSerializer(data=doc_data)
                if serializer.is_valid():
                    doc_serializers.append(serializer)
                else:
                    raise serializers.ValidationError(response.make_errors(serializer))
        render = self.context.get('render')
        if render:
            doc_data = {
                'project': instance.id,
                'document': render
            }
            old_render = Render360.objects.get(project=instance)
            old_render.project = None
            old_render.save()
            serializer = Render360Serializer(data=doc_data)
            if serializer.is_valid():
                try:
                    upload.delete_file(old_render.document)
                    old_render.delete()
                except:
                    pass
                serializer.save()
            else:
                old_render.project = instance
                old_render.save()
                raise serializers.ValidationError(response.make_errors(serializer))
        delete_documents = self.context.get('delete_documents')
        for del_doc in delete_documents:
            path = del_doc
            first_pos = path.rfind("/")
            last_pos = len(path)
            name = path[first_pos + 1:last_pos]
            doc_objects = ProjectDocument.objects.filter(project=instance)
            for doc in doc_objects:
                if doc.filename() == name:
                    upload.delete_file(doc.document)
                    doc.delete()
        for serializer in doc_serializers:
            serializer.save()
        instance.name = validated_data.get('name', instance.name)
        instance.area = validated_data.get('area', instance.area)
        instance.price_from = validated_data.get('price_from', instance.price_from)
        instance.price_to = validated_data.get('price_to', instance.price_to)
        instance.description = validated_data.get('description', instance.description)
        if category:
            instance.category = category
        if style:
            instance.style = style
        if purpose:
            instance.purpose = purpose
        if type:
            instance.type = type
        if validated_data.get('tags'):
            instance.tags.clear()
            for tag in validated_data.get('tags'):
                instance.tags.add(tag)
        instance.save()
        return instance


class ProjectForUpdateSerializer(serializers.ModelSerializer):
    category = ProjectCategoryShortSerializer()
    purpose = ProjectPurposeShortSerializer()
    type = ProjectTypeSerializer()
    style = ProjectStyleSerializer()
    tags = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    render = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('name', 'name', 'category', 'purpose', 'type', 'style', 'area', 'price_from', 'price_to', 'description',
                  'tags', 'documents', 'render')

    def get_documents(self, obj):
        urls = []
        project_documents = ProjectDocument.objects.filter(project=obj)
        for doc in project_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls

    def get_render(self, obj):
        try:
            render = Render360.objects.get(project=obj)
            return self.context.build_absolute_uri(render.document.url)
        except:
            return None

    def get_tags(self, obj):
        serializer = ProjectTagShortSerializer(obj.tags.all(), many=True)
        return serializer.data


class ProjectCommentDetailSerializer(serializers.ModelSerializer):
    user = UserShortAvatarSerializer()
    creation_date = serializers.DateTimeField(format=constants.DATETIME_FORMAT)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()

    class Meta:
        model = ProjectComment
        fields = ('id', 'user', 'creation_date', 'rating', 'text', 'likes_count', 'is_liked', 'is_author')

    def get_likes_count(self, obj):
        return obj.likes_count

    def get_is_liked(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if obj.user_likes.filter(id=user.id).count() > 0:
                return True
            else:
                return False
        return None

    def get_is_author(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if user == obj.user:
                return True
            else:
                return False
        return None


class ProjectDetailSerializer(ProjectModalSerializer):
    user = UserMediumSerializer()
    views_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    class Meta(ProjectModalSerializer.Meta):
        fields = ProjectModalSerializer.Meta.fields + (
            'name', 'user', 'views_count', 'comments_count', 'favorites_count',
            'description',)

    def get_views_count(self, obj):
        return obj.views.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_favorites_count(self, obj):
        return obj.user_favorites.count()


class ProjectCommentReplyListSerializer(serializers.ModelSerializer):
    user = UserShortAvatarSerializer()
    creation_date = serializers.DateTimeField(format=constants.DATETIME_FORMAT)
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectCommentReply
        fields = ('id', 'user', 'text', 'creation_date', 'likes_count', 'is_liked', 'photos', 'is_author')

    def get_likes_count(self, obj):
        return obj.likes_count

    def get_is_liked(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if obj.user_likes.filter(id=user.id).count() > 0:
                return True
            else:
                return False
        return None

    def get_is_author(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if user == obj.user:
                return True
            else:
                return False
        return None
      
    def get_photos(self, obj):
        urls = []
        comment_documents = ProjectCommentReplyDocument.objects.filter(reply=obj)
        for doc in comment_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls


class ProjectCommentWithReplySerializer(ProjectCommentDetailSerializer):
    reply = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta(ProjectCommentDetailSerializer.Meta):
        fields = ProjectCommentDetailSerializer.Meta.fields + ('photos', 'reply')

    def get_reply(self, obj):
        try:
            reply = obj.reply
            serializer = ProjectCommentReplyListSerializer(reply, context=self.context)
            return serializer.data
        except:
            return None

    def get_photos(self, obj):
        urls = []
        comment_documents = ProjectCommentDocument.objects.filter(comment=obj)
        for doc in comment_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls


class ProjectCommentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCommentDocument
        fields = '__all__'


class ProjectCommentReplyDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCommentReplyDocument
        fields = '__all__'


class ProjectCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectComment
        fields = '__all__'
        read_only_fields = ['project', 'user']

    def create(self, validated_data):
        validated_data.pop('user_likes')
        comment = ProjectComment.objects.create(**validated_data)
        documents = self.context.get('documents')
        if documents:
            if len(documents) > 6:
                raise serializers.ValidationError(f'{constants.RESPONSE_MAX_FILES} 6')
            for doc in documents:
                data = {
                    'document': doc,
                    'comment': comment.id
                }
                serializer = ProjectCommentDocumentSerializer(data=data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    comment.delete()
                    raise serializers.ValidationError(response.make_errors(serializer))
        return comment


class ProjectCommentReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCommentReply
        fields = '__all__'
        read_only_fields = ['comment', 'user']

    def create(self, validated_data):
        validated_data.pop('user_likes')
        reply = ProjectCommentReply.objects.create(**validated_data)
        documents = self.context.get('documents')
        doc_serializers = []
        if documents:
            if len(documents) > 6:
                raise serializers.ValidationError(f'{constants.RESPONSE_MAX_FILES} 6')
            for doc in documents:
                data = {
                    'document': doc,
                    'reply': reply.id
                }
                serializer = ProjectCommentReplyDocumentSerializer(data=data)
                if serializer.is_valid():
                    doc_serializers.append(serializer)
                else:
                    reply.delete()
                    raise serializers.ValidationError(response.make_errors(serializer))
        for serializer in doc_serializers:
            serializer.save()
        return reply
