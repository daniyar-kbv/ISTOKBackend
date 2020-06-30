from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser
from main.models import Project, ProjectDocument, ProjectUserFavorite, ProjectComment, ProjectView, ProjectCommentReply, \
    ProjectCommentDocument
from users.models import ProjectCategory, ProjectType, ProjectStyle, ProjectPurpose, ProjectPurposeSubType, ProjectTag, \
    ProjectPurposeType, MerchantProfile
from users.models import Country, City
from users.serializers import UserShortSerializer, UserMediumSerializer, UserShortAvatarSerializer
from utils import response
from profiles.models import Application
import constants, math


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


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


class ProjectCategorySerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = ProjectCategory
        fields = ('name', 'description', 'photo')

    def get_photo(self, obj):
        if obj.image:
            return self.context.build_absolute_uri(obj.image.url)
        return None


class ProjectPurposeSubtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPurposeSubType
        fields = '__all__'


class ProjectPurposeTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectPurposeType
        fields = '__all__'


class ProjectPurposeSerializer(serializers.ModelSerializer):
    type = ProjectPurposeTypeSerializer()
    subtype = ProjectPurposeSubtypeSerializer()

    class Meta:
        model = ProjectPurpose
        fields = '__all__'


class ProjectTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectType
        fields = '__all__'


class ProjectStyleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectStyle
        fields = '__all__'


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


class ProjectSearchSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    is_favorite = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    price_from_full = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ('id', 'user', 'name', 'price_from_full', 'rating', 'is_favorite', 'is_top', 'is_detailed',
                  'photo')

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


class ProjectDetailListSerializer(ProjectSearchSerializer):
    user = UserShortAvatarSerializer()


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

    class Meta:
        model = ProjectCommentReply
        fields = ('id', 'user', 'text', 'creation_date', 'likes_count', 'is_liked', 'is_author')

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
