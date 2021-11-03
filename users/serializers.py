from rest_framework import serializers
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from users.models import MainUser, ClientProfile, MerchantProfile, MerchantPhone, CodeVerification, ProfileDocument, \
    MerchantReview, ReviewReply, ReviewDocument, Specialization, ClientRating, ReviewReplyDocument
from main.models import Project, ProjectDocument, ProjectTag, ProjectCategory
from utils import response, validators

import constants, re, math, logging

logger = logging.getLogger(__name__)


class ProjectCategoryShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCategory
        fields = ('id', 'name')


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ('id', 'name')


class SpecializationWithCategorySerializer(SpecializationSerializer):
    category = ProjectCategoryShortSerializer()

    class Meta(SpecializationSerializer.Meta):
        fields = SpecializationSerializer.Meta.fields + ('category', )


class ProjectTagShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTag
        fields = ('id', 'name')


class UserShortSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ('id', 'name')

    def get_name(self, obj):
        return f'{obj.get_full_name()}'


class UserShortRatingSerializer(UserShortSerializer):
    rating = serializers.SerializerMethodField()

    class Meta(UserShortSerializer.Meta):
        fields = UserShortSerializer.Meta.fields + ('rating', )

    def get_rating(self, obj):
        profile = obj.profile
        if profile:
            return profile.rating
        return None


class UserShortAvatarSerializer(UserShortSerializer):
    avatar = serializers.SerializerMethodField()
    is_pro = serializers.SerializerMethodField()

    class Meta(UserShortSerializer.Meta):
        fields = UserShortSerializer.Meta.fields + ('avatar', 'is_pro')

    def get_avatar(self, obj):
        try:
            profile = obj.client_profile
        except:
            try:
                profile = obj.merchant_profile
            except:
                return None
        if profile.avatar:
            return self.context.build_absolute_uri(profile.avatar.url)
        return None

    def get_is_pro(self, obj):
        try:
            return obj.merchant_profile.is_pro
        except:
            None


class UserMediumSerializer(UserShortAvatarSerializer):
    tags = serializers.SerializerMethodField()

    class Meta(UserShortAvatarSerializer.Meta):
        fields = UserShortAvatarSerializer.Meta.fields + ('is_pro', 'tags')

    def get_tags(self, obj):
        tags = obj.merchant_profile.tags
        serializer = ProjectTagShortSerializer(tags, many=True)
        return serializer.data


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        return validators.validate_phone(value)


class UserClientCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=True)

    class Meta:
        model = MainUser
        fields = ('email', 'password', 'role')

    def validate_password(self, value):
        return validators.validate_password(value)

    def create(self, validated_data):
        user = MainUser.objects.create_user(**validated_data)
        return user


class ClientProfileCreateSerializer(serializers.ModelSerializer):
    user = UserClientCreateSerializer(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = ClientProfile
        fields = ('first_name', 'last_name', 'date_of_birth', 'user')

    def create(self, validated_data):
        user_data = self.context['user']
        serializer = UserClientCreateSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save()
        else:
            logger.error(
                f'Registration with email: ({constants.ROLES[0]}) failed. {response.make_errors_new(serializer)}')
            raise serializers.ValidationError(serializer.errors)
        profile = ClientProfile.objects.create(user=user, **validated_data)
        if settings.DEBUG:
            if self.context['avatar']:
                profile.avatar = self.context['avatar']
                profile.save()
            if self.context['rating']:
                profile.rating = float(self.context['rating'])
                profile.save()
        return profile


class ProfileDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfileDocument
        fields = ('user', 'document')


class MerchantProfileCreateSerializer(serializers.ModelSerializer):
    user = UserClientCreateSerializer(required=False)

    class Meta:
        model = MerchantProfile
        fields = '__all__'

    def create(self, validated_data):
        user_data = self.context['user']
        if user_data:
            serializer = UserClientCreateSerializer(data=user_data)
            if serializer.is_valid():
                user = MainUser.objects.create_user(**user_data)
            else:
                raise serializers.ValidationError(serializer.errors)
        if self.context['phones']:
            for phone in self.context['phones']:
                serializer = PhoneSerializer(data={
                    'phone': phone
                })
                if serializer.is_valid():
                    try:
                        merchant_phone = MerchantPhone.objects.get(phone=phone)
                    except MerchantPhone.DoesNotExist:
                        user.delete()
                        raise serializers.ValidationError(
                            response.make_messages_new([('phone', constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST)])
                        )
                    if merchant_phone.user is not None:
                        user.delete()
                        raise serializers.ValidationError(
                            response.make_messages_new([('phone', f'{phone} {constants.RESPONSE_PHONE_REGISTERED}')])

                        )
                    if not merchant_phone.is_valid:
                        user.delete()
                        raise serializers.ValidationError(
                            response.make_messages_new([('phone', constants.VALIDATION_PHONE_NOT_VERIFIED)])
                        )
                    merchant_phone.user = user
                    merchant_phone.save()
                else:
                    user.delete()
                    raise serializers.ValidationError(serializer.errors)
        documents = self.context.get('documents')
        if documents:
            if len(documents) > 6:
                user.delete()
                raise serializers.ValidationError(
                    response.make_messages_new([('documents', f'{constants.RESPONSE_MAX_FILES} 6')])
                )
            for document in documents:
                doc_data = {
                    'user': user.id,
                    'document': document
                }
                serializer = ProfileDocumentCreateSerializer(data=doc_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    user.delete()
                    raise serializers.ValidationError(serializer.errors)
        categories = validated_data.pop('categories')
        specializations = validated_data.pop('specializations')
        tags = validated_data.pop('tags')
        profile = MerchantProfile.objects.create(user=user, **validated_data)
        for category in categories:
            profile.categories.add(category)
        for specialization in specializations:
            profile.specializations.add(specialization)
        for tag in tags:
            profile.tags.add(tag)
        if settings.DEBUG:
            if self.context['avatar']:
                profile.avatar = self.context['avatar']
                profile.save()
            if self.context['rating']:
                profile.rating = float(self.context['rating'])
                profile.save()
        return profile


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(required=False)
    phone = serializers.CharField(required=False)

    class Meta:
        model = MainUser
        fields = ('email', 'phone', 'password')

    def validate_email(self, value):
        if value == '' or value is None:
            raise serializers.ValidationError(
                response.make_messages_new([('email', constants.VALIDATION_CANT_BE_BLANK)])
            )
        return value

    def validate_phone(self, value):
        regex = constants.PHONE_FORMAT
        if not isinstance(value, str) or re.search(regex, value) is None:
            raise serializers.ValidationError(
                response.make_messages_new([('phone', constants.VALIDATION_PHONE_FORMAT_ERROR)])
            )
        return value


class MerchantPhoneVerification(serializers.ModelSerializer):
    class Meta:
        model = MerchantPhone
        fields = '__all__'

    def validate_phone(self, value):
        regex = constants.PHONE_FORMAT
        if not isinstance(value, str) or re.search(regex, value) is None:
            raise serializers.ValidationError(
                response.make_messages_new([('phone', constants.VALIDATION_PHONE_FORMAT_ERROR)])
            )
        return value


class CodeVerificationSerializer(serializers.ModelSerializer):
    phone = MerchantPhoneVerification()

    class Meta:
        model = CodeVerification
        fields = '__all__'

    def validate_code(self, value):
        for char in value:
            if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                raise serializers.ValidationError(
                    response.make_messages_new([('phone', constants.VALIDATION_PHONE_FORMAT_ERROR)])
                )
        if len(value) != 4:
            raise serializers.ValidationError(
                response.make_messages_new([('phone', constants.VALIDATION_PHONE_FORMAT_ERROR)])
            )
        return value

    def create(self, validated_data):
        phone = validated_data.pop('phone').get('phone')
        if MerchantPhone.objects.filter(phone=phone).count() > 0:
            try:
                merchant_phone = MerchantPhone.objects.get(phone=phone)
            except MerchantPhone.DoesNotExist:
                raise serializers.ValidationError(
                    response.make_messages_new([('server', constants.RESPONSE_SERVER_ERROR)])
                )
        else:
            merchant_phone = MerchantPhone.objects.create(phone=phone)
        try:
            if merchant_phone.verification:
                verification = merchant_phone.verification
                verification.delete()
        except:
            pass
        CodeVerification.objects.create(phone=merchant_phone, **validated_data)
        return CodeVerification


class MerchantMainPageSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    specialization_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = MerchantProfile
        fields = ('user_id', 'user_name', 'rating', 'photo', 'avatar', 'specialization_name')

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def get_photo(self, obj):
        project = Project.objects.filter(user=obj.user).first()
        if project:
            photo = ProjectDocument.objects.filter(project=project).first()
            if photo:
                return self.context.build_absolute_uri(photo.document.url)
            return None

    def get_specialization_name(self, obj):
        try:
            return obj.specializations.first().name
        except:
            return None

    def get_avatar(self, obj):
        if obj.avatar:
            return self.context.build_absolute_uri(obj.avatar.url)
        return None


class ReviewMainPageSerializer(serializers.ModelSerializer):
    user = UserShortAvatarSerializer()
    creation_date = serializers.DateTimeField(format=constants.DATETIME_FORMAT)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = MerchantReview
        fields = ('id', 'user', 'creation_date', 'likes_count', 'is_liked', 'text', 'rating')

    def get_is_liked(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if obj.user_likes.filter(id=user.id).count() > 0:
                return True
            else:
                return False
        return None

    def get_likes_count(self, obj):
        return obj.user_likes.count()


class MerchantReviewReplyDetailListSerializer(serializers.ModelSerializer):
    user = UserShortAvatarSerializer()
    creation_date = serializers.DateTimeField(format=constants.DATETIME_FORMAT)
    is_liked = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()

    class Meta:
        model = ReviewReply
        fields = ('id', 'user', 'creation_date', 'likes_count', 'is_liked', 'text', 'photos')

    def get_is_liked(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if obj.user_likes.filter(id=user.id).count() > 0:
                return True
            else:
                return False
        return None

    def get_likes_count(self, obj):
        return obj.user_likes.count()

    def get_photos(self, obj):
        urls = []
        comment_documents = ReviewReplyDocument.objects.filter(reply=obj)
        for doc in comment_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls


class MerchantReviewDetailList(ReviewMainPageSerializer):
    photos = serializers.SerializerMethodField()
    reply = serializers.SerializerMethodField()

    class Meta(ReviewMainPageSerializer.Meta):
        fields = ReviewMainPageSerializer.Meta.fields + ('photos', 'reply')

    def get_photos(self, obj):
        urls = []
        comment_documents = ReviewDocument.objects.filter(review=obj)
        for doc in comment_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls

    def get_reply(self, obj):
        try:
            reply = obj.reply
            serializer = MerchantReviewReplyDetailListSerializer(reply, context=self.context)
            return serializer.data
        except:
            return None


class UserSearchSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    specialization_name = serializers.SerializerMethodField()
    projects_count = serializers.SerializerMethodField()
    tags_count = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    price_from_full = serializers.SerializerMethodField()
    description_short = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    is_pro = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ('id', 'full_name', 'specialization_name', 'projects_count', 'tags_count', 'reviews_count', 'city',
                  'avatar', 'price_from_full', 'description_short', 'rating', 'is_pro')

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_specialization_name(self, obj):
        try:
            return obj.merchant_profile.specializations.first().name
        except:
            return None

    def get_projects_count(self, obj):
        return obj.projects.count()

    def get_tags_count(self, obj):
        return obj.merchant_profile.tags.count()

    def get_reviews_count(self, obj):
        print(obj)
        reviews = MerchantReview.objects.filter(merchant=obj)
        return reviews.count()

    def get_city(self, obj):
        return obj.merchant_profile.city.name

    def get_avatar(self, obj):
        if obj.merchant_profile.avatar:
            return self.context['request'].build_absolute_uri(obj.profile.avatar.url)
        return None

    def get_price_from_full(self, obj):
        try:
            price_from = obj.projects.order_by('price_from').first().price_from
            price = int(price_from) if price_from % math.trunc(price_from) == 0 else price_from
            return price
        except:
            return None

    def get_description_short(self, obj):
        return obj.merchant_profile.description_short

    def get_rating(self, obj):
        return obj.merchant_profile.rating

    def get_is_pro(self, obj):
        return obj.merchant_profile.is_pro


class UserTopDetailSerializer(UserSearchSerializer):
    reviews_count = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()

    class Meta(UserSearchSerializer.Meta):
        fields = UserSearchSerializer.Meta.fields + ('reviews_count', 'url')

    def get_reviews_count(self, obj):
        return MerchantReview.objects.filter(merchant=obj).count()

    def get_url(self, obj):
        try:
            return obj.merchant_profile.url
        except:
            return None


class MerchantDetailSerializer(serializers.ModelSerializer):
    documents = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    description_full = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ('id', 'description_full', 'documents', 'tags')

    def get_documents(self, obj):
        urls = []
        comment_documents = ProfileDocument.objects.filter(user=obj)
        for doc in comment_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls

    def get_tags(self, obj):
        try:
            tags = obj.merchant_profile.tags
            serializer = ProjectTagShortSerializer(tags, many=True)
            return serializer.data
        except:
            return []

    def get_description_full(self, obj):
        try:
            return obj.merchant_profile.description_full
        except:
            return None


class MerchantReviewDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewDocument
        fields = '__all__'


class MerchantReviewReplyDocumentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReplyDocument
        fields = '__all__'


class MerchantReviewCreateSerializer(serializers.ModelSerializer):
    rating = serializers.FloatField(required=True)

    class Meta:
        model = MerchantReview
        fields = ('rating', 'text')

    def create(self, validated_data):
        review = MerchantReview.objects.create(**validated_data)

        documents = self.context.get('documents')
        if documents:
            if len(documents) > 6:
                raise serializers.ValidationError(f'{constants.RESPONSE_MAX_FILES} 6')
            for document in documents:
                doc_data = {
                    'review': review.id,
                    'document': document,
                    'user': self.context.get('user').id
                }
                serializer = MerchantReviewDocumentCreateSerializer(data=doc_data)
                if serializer.is_valid():
                    serializer.save()
                else:
                    review.delete()
                    raise serializers.ValidationError(response.make_errors_new(serializer))
        return review

    def validate_rating(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError(
                response.make_messages_new([('rating', constants.VALIDATION_RATING_RANGE)])
            )
        return value


class MerchantReviewReplyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = ('text', )

    def create(self, validated_data):
        reply = ReviewReply.objects.create(**validated_data)

        documents = self.context.get('documents')
        doc_serializers = []
        if documents:
            if len(documents) > 6:
                raise serializers.ValidationError(f'{constants.RESPONSE_MAX_FILES} 6')
            for document in documents:
                doc_data = {
                    'reply': reply.id,
                    'document': document,
                    'user': self.context.get('user').id
                }
                serializer = MerchantReviewReplyDocumentCreateSerializer(data=doc_data)
                if serializer.is_valid():
                    doc_serializers.append(serializer)
                else:
                    reply.delete()
                    raise serializers.ValidationError(response.make_errors_new(serializer))
        for serializer in doc_serializers:
            serializer.save()
        return reply


class ClientRatingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientRating
        fields = ('rating', )

    def validate_rating(self, value):
        if value < 0 or value > 10:
            raise serializers.ValidationError(
                response.make_messages_new([('rating', constants.VALIDATION_RATING_RANGE)])
            )
        return value
