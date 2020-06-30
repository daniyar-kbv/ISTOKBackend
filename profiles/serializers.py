from rest_framework import serializers
from users.models import MainUser, ClientProfile, MerchantReview, ProjectCategory, ProfileDocument
from users.serializers import PhoneSerializer, MerchantPhone, UserShortRatingSerializer, MerchantProfile, \
    ProfileDocumentCreateSerializer, SpecializationWithCategorySerializer
from profiles.models import FormAnswer, FormQuestion, FormQuestionGroup, FormUserAnswer, Application, \
    ApplicationDocument, PaidFeatureType, UsersPaidFeature, ProjectPaidFeature, Notification
from main.models import ProjectUserFavorite
from main.serializers import ProjectCategoryShortSerializer, CitySerializer, ProjectTagSerializer
from utils import response, upload, validators, general
from datetime import datetime
import constants, os


class ClientProfileGetSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ('id', 'avatar', 'first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'rating')

    def get_avatar(self, obj):
        try:
            profile = obj.client_profile
        except:
            try:
                profile = obj.merchant_profile
            except:
                raise serializers.ValidationError(constants.RESPONSE_SERVER_ERROR)
        if profile.avatar:
            return self.context.build_absolute_uri(profile.avatar.url)
        return None

    def get_first_name(self, obj):
        return obj.profile.first_name

    def get_last_name(self, obj):
        return obj.profile.last_name

    def get_phone(self, obj):
        phone_obj = obj.phones.first()
        if phone_obj:
            return phone_obj.phone
        return None

    def get_date_of_birth(self, obj):
        return obj.profile.date_of_birth

    def get_rating(self, obj):
        return obj.profile.rating


class ClientProfileMerchantSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    since = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ('id', 'avatar', 'full_name', 'age', 'since', 'rating')

    def get_avatar(self, obj):
        try:
            profile = obj.client_profile
        except:
            try:
                profile = obj.merchant_profile
            except:
                raise serializers.ValidationError(constants.RESPONSE_SERVER_ERROR)
        if profile.avatar:
            return self.context.build_absolute_uri(profile.avatar.url)
        return None

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_rating(self, obj):
        return obj.profile.rating

    def get_age(self, obj):
        today = datetime.today()
        return today.year - obj.profile.date_of_birth.year - ((today.month, today.day) < (obj.profile.date_of_birth.month, obj.profile.date_of_birth.day))

    def get_since(self, obj):
        return obj.creation_date.strftime(constants.DATE_FORMAT)


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainUser
        fields = ('email', )


class ClientProfileUpdateSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(format=constants.DATE_FORMAT, required=False)

    class Meta:
        model = ClientProfile
        fields = ('avatar', 'first_name', 'last_name', 'date_of_birth')

    def update(self, instance, validated_data):
        user_data = self.context.get('user_data')
        user = instance.user
        if user_data:
            serializer = UserUpdateSerializer(user, data=user_data)
            if serializer.is_valid():
                user = serializer.save()
            else:
                raise serializers.ValidationError(response.make_errors(serializer))
        if self.context.get('phone'):
            phone = self.context.get('phone')
            serializer = PhoneSerializer(data={
                'phone': phone
            })
            if serializer.is_valid():
                try:
                    merchant_phone = MerchantPhone.objects.get(phone=phone)
                except MerchantPhone.DoesNotExist:
                    raise serializers.ValidationError(response.make_messages([constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST]))
                if merchant_phone.user is not None:
                    raise serializers.ValidationError(response.make_messages([f'{phone} {constants.RESPONSE_PHONE_REGISTERED}']))
                if not merchant_phone.is_valid:
                    raise serializers.ValidationError(response.make_messages([constants.VALIDATION_PHONE_NOT_VERIFIED]))
                phones = MerchantPhone.objects.filter(user=user)
                for p in phones:
                    if p != merchant_phone:
                        p.delete()
                merchant_phone.user = user
                merchant_phone.save()
            else:
                raise serializers.ValidationError(response.make_errors(serializer))
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        avatar = validated_data.get('avatar')
        if avatar:
            upload.delete_folder(instance.avatar)
        instance.avatar = validated_data.get('avatar', instance.avatar)
        instance.date_of_birth = validated_data.get('date_of_birth', instance.date_of_birth)
        instance.save()
        return instance


class MerchantProfileTopSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    specialization = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    url = serializers.SerializerMethodField()
    description_short = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ('id', 'full_name', 'specialization', 'avatar', 'city', 'url', 'description_short', 'rating', )

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_specialization(self, obj):
        if isinstance(obj.profile, MerchantProfile):
            spec = obj.profile.specializations.first()
            if spec:
                return spec.name
        return None

    def get_avatar(self, obj):
        if obj.merchant_profile.avatar:
            return self.context.build_absolute_uri(obj.profile.avatar.url)
        return None

    def get_city(self, obj):
        return obj.profile.city.name

    def get_url(self, obj):
        return obj.profile.url

    def get_description_short(self, obj):
        return obj.profile.description_short

    def get_rating(self, obj):
        return obj.profile.rating


class MerchantProfileGetSerializer(serializers.ModelSerializer):
    description_full = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = MainUser
        fields = ('description_full', 'documents', 'tags')

    def get_description_full(self, obj):
        return obj.profile.description_full

    def get_documents(self, obj):
        urls = []
        documents = ProfileDocument.objects.filter(user=obj)
        for doc in documents:
            urls.append(self.context.build_absolute_uri(doc.url))
        return urls

    def get_tags(self, obj):
        names = []
        tags = obj.profile.tags.all()
        for tag in tags:
            names.append(tag.name)
        return names


class MerchantProfileForUpdate(serializers.ModelSerializer):
    specializations = serializers.SerializerMethodField()
    city = CitySerializer()
    email = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField
    phones = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()

    class Meta:
        model = MerchantProfile
        fields = ('first_name', 'last_name', 'company_name', 'city', 'address', 'email', 'specializations', 'tags',
                  'description_short', 'description_full', 'url', 'phones', 'documents_description', 'documents')

    def get_specializations(self, obj):
        specializations = []
        specialization_objects = obj.specializations.all()
        for specialization in specialization_objects:
            serializer = SpecializationWithCategorySerializer(specialization)
            specializations.append(serializer.data)
        return specializations

    def get_tags(self, obj):
        tags = []
        tag_objects = obj.tags.all()
        for tag in tag_objects:
            serializer = SpecializationWithCategorySerializer(tag)
            tags.append(serializer.data)
        return tags

    def get_email(self, obj):
        return obj.user.email

    def get_phones(self, obj):
        phones = []
        phones_objects = MerchantPhone.objects.filter(user=obj.user)
        for phone in phones_objects:
            if phone.is_valid:
                phones.append(phone.phone)
        return phones

    def get_documents(self, obj):
        urls = []
        documents = ProfileDocument.objects.filter(user=obj.user)
        for doc in documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls


class MerchantProfileUpdate(serializers.ModelSerializer):
    class Meta:
        model = MerchantProfile
        fields = ('first_name', 'last_name', 'company_name', 'city', 'address', 'specializations', 'tags',
                  'categories', 'description_short', 'description_full', 'url', 'documents_description')

    def update(self, instance, validated_data):
        user = instance.user
        phones = []
        if self.context['phones']:
            for phone in self.context['phones']:
                serializer = PhoneSerializer(data={
                    'phone': phone
                })
                if serializer.is_valid():
                    try:
                        merchant_phone = MerchantPhone.objects.get(phone=phone)
                    except MerchantPhone.DoesNotExist:
                        raise serializers.ValidationError(
                            response.make_messages([constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST]))
                    if merchant_phone.user != user and merchant_phone.user is not None:
                        raise serializers.ValidationError(
                            response.make_messages([f'{phone} {constants.RESPONSE_PHONE_REGISTERED}']))
                    if not merchant_phone.is_valid:
                        raise serializers.ValidationError(
                            response.make_messages([constants.VALIDATION_PHONE_NOT_VERIFIED]))
                    phones.append(merchant_phone)
                else:
                    raise serializers.ValidationError(response.make_errors(serializer))
        documents = self.context.get('documents')
        doc_serializers = []
        if documents:
            for document in documents:
                doc_data = {
                    'user': user.id,
                    'document': document
                }
                serializer = ProfileDocumentCreateSerializer(data=doc_data)
                if serializer.is_valid():
                    doc_serializers.append(serializer)
                else:
                    raise serializers.ValidationError(response.make_errors(serializer))
        email = self.context.get('email')
        if email:
            try:
                usr = MainUser.objects.get(email=email)
                if usr != user:
                    raise serializers.ValidationError(response.make_messages([constants.VALIDATION_EMAIL_EXISTS]))
            except:
                user.email = email
                user.save()
        for merchant_phone in phones:
            merchant_phone.user = user
            merchant_phone.save()
        delete_documents = self.context.get('delete_documents')
        for del_doc in delete_documents:
            path = del_doc
            first_pos = path.rfind("/")
            last_pos = len(path)
            name = path[first_pos + 1:last_pos]
            doc_objects = ProfileDocument.objects.filter(user=user)
            for doc in doc_objects:
                if doc.filename() == name:
                    upload.delete_file(doc.document)
                    doc.delete()
        for serializer in doc_serializers:
            serializer.save()
        categories = validated_data.pop('categories')
        specializations = validated_data.pop('specializations')
        tags = validated_data.pop('tags')
        instance.specializations.clear()
        instance.categories.clear()
        instance.tags.clear()
        for specialization in specializations:
            instance.specializations.add(specialization)
        for category in categories:
            instance.categories.add(category)
        for tag in tags:
            instance.tags.add(tag)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.company_name = validated_data.get('company_name', instance.company_name)
        instance.city = validated_data.get('city', instance.city)
        instance.address = validated_data.get('first_name', instance.address)
        instance.description_short = validated_data.get('description_short', instance.description_short)
        instance.description_full = validated_data.get('description_full', instance.description_full)
        instance.url = validated_data.get('url', instance.url)
        instance.documents_description = validated_data.get('documents_description', instance.documents_description)
        instance.save()
        return instance


class UserChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainUser
        fields = ('password', )

    def validate_password(self, value):
        return validators.validate_password(value)

    def update(self, instance, validated_data):
        instance.set_password(validated_data.get('password', instance.password))
        instance.save()
        return instance


class FormAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAnswer
        fields = ('id', 'answer', 'position')


class FormQuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = FormQuestion
        fields = ('id', 'question', 'position', 'type', 'answers')

    def get_answers(self, obj):
        answers = FormAnswer.objects.filter(question=obj)
        serializer = FormAnswerSerializer(answers, many=True)
        return serializer.data


class FormQuestionGroupSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = FormQuestionGroup
        fields = ('id', 'name', 'position', 'questions')

    def get_questions(self, obj):
        questions = FormQuestion.objects.filter(group=obj)
        serializer = FormQuestionSerializer(questions, many=True)
        return serializer.data


class FormUserAnswerCreatePostSerializer(serializers.Serializer):
    answers = serializers.ListField(child=serializers.IntegerField(min_value=0))

    def create(self, validated_data):
        answers = validated_data.get('answers')
        answers_objects = []
        for answer in answers:
            try:
                answer_obj = FormAnswer.objects.get(id=answer)
                answers_objects.append(answer_obj)
            except:
                raise serializers.ValidationError(response.make_messages(
                    [f'Ответ {answer} {constants.RESPONSE_DOES_NOT_EXIST}'])
                )
        questions = FormQuestion.objects.all()
        for answer in answers_objects:
            if questions.filter(question=answer.question.question).count() > 0:
                questions.exclude(question=answer.question.question)
        if questions.count() > 0:
            raise serializers.ValidationError(response.make_messages([constants.VALIDATION_FORM_NOT_COMPLETE]))
        user = self.context.user
        existing_answers = FormUserAnswer.objects.filter(user=user)
        existing_answers.delete()
        for answer in answers_objects:
            FormUserAnswer.objects.create(user=user, answer=answer)
        return answers_objects


class ApplicationBaseSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    creation_date = serializers.DateTimeField(format=constants.DATETIME_FORMAT)
    client = UserShortRatingSerializer()
    merchant = UserShortRatingSerializer()
    category = serializers.SerializerMethodField()
    document_names = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = ('id', 'status', 'creation_date', 'client', 'merchant', 'category', 'document_names', 'comment')

    def get_status(self, obj):
        if obj.status == constants.APPLICATION_CONFIRMED:
            return 'В процессе'
        if obj.status == constants.APPLICATION_FINISHED_CONFIRMED:
            return 'Завершена'
        if obj.status == constants.APPLICATION_DECLINED_MERCHANT or obj.status == constants.APPLICATION_DECLINED_CLIENT:
            return 'Отклонена'
        if self.context:
            user = self.context.user
            if user.role == constants.ROLE_CLIENT:
                if obj.status == constants.APPLICATION_CREATED or obj.status == constants.APPLICATION_FINISHED:
                    return 'Ожидает ответа'
            elif user.role == constants.ROLE_MERCHANT:
                if obj.status == constants.APPLICATION_CREATED:
                    return 'Новая'
                elif obj.status == constants.APPLICATION_FINISHED:
                    return 'Ожидает завершения'
        return None

    def get_category(self, obj):
        return obj.category.name

    def get_document_names(self, obj):
        names = []
        project_documents = ApplicationDocument.objects.filter(application=obj)
        for doc in project_documents:
            names.append(os.path.basename(doc.document.name))
        return f'{"(%d) "%(len(names)) if len(names) > 0 else ""}{", ".join(names)}'


class ApplicationClientConfirmedSerializer(ApplicationBaseSerializer):
    phone = serializers.SerializerMethodField()

    class Meta(ApplicationBaseSerializer.Meta):
        fields = ApplicationBaseSerializer.Meta.fields + ('phone', )

    def get_phone(self, obj):
        phones = MerchantPhone.objects.filter(user=obj.merchant)
        if phones.first():
            return phones.first().phone
        return None


class ApplicationClientFinishedSerializer(ApplicationBaseSerializer):
    class Meta(ApplicationBaseSerializer.Meta):
        fields = ApplicationBaseSerializer.Meta.fields + ('rating', )


class ApplicationDeclinedSerializer(ApplicationBaseSerializer):
    decline_reason = serializers.SerializerMethodField()

    class Meta(ApplicationBaseSerializer.Meta):
        fields = ApplicationBaseSerializer.Meta.fields + ('decline_reason', )

    def get_decline_reason(self, obj):
        if self.context:
            if self.context.user:
                if obj.status == constants.APPLICATION_DECLINED_CLIENT:
                    if self.context.user.role == constants.ROLE_CLIENT:
                        return 'Отклонено вами'
                    else:
                        return 'Отклонено клиентом'
                elif obj.status == constants.APPLICATION_DECLINED_MERCHANT:
                    if self.context.user.role == constants.ROLE_MERCHANT:
                        return 'Отклонено вами'
        return obj.decline_reason


class ApplicationMerchantConfirmedDeclinedWaitingSerializer(ApplicationBaseSerializer):
    phone = serializers.SerializerMethodField()

    class Meta(ApplicationBaseSerializer.Meta):
        fields = ApplicationBaseSerializer.Meta.fields + ('phone', )

    def get_phone(self, obj):
        phones = MerchantPhone.objects.filter(user=obj.client)
        if phones.first():
            return phones.first().phone
        return None


class ApplicationDeclineSerializer(serializers.ModelSerializer):
    decline_reason = serializers.CharField(required=True)

    class Meta:
        model = Application
        fields = ('decline_reason', )

    def update(self, instance, validated_data):
        instance.decline_reason = validated_data.get('decline_reason', instance.decline_reason)
        instance.status = constants.APPLICATION_DECLINED_MERCHANT
        instance.save()
        return instance


class ApplicationDetailSerializer(ApplicationBaseSerializer):
    photos = serializers.SerializerMethodField()
    has_form = serializers.SerializerMethodField()

    class Meta(ApplicationBaseSerializer.Meta):
        fields = ApplicationBaseSerializer.Meta.fields + ('photos', 'has_form', )

    def get_photos(self, obj):
        urls = []
        comment_documents = ApplicationDocument.objects.filter(application=obj)
        for doc in comment_documents:
            urls.append(self.context.build_absolute_uri(doc.document.url))
        return urls

    def get_has_form(self, obj):
        if FormUserAnswer.objects.filter(user=obj.client).count() > 0:
            return True
        return False


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDocument
        fields = '__all__'


class ApplicationCreateSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(required=True, write_only=True)

    class Meta:
        model = Application
        fields = ('category', 'comment')

    def create(self, validated_data):
        try:
            category = ProjectCategory.objects.get(id=validated_data.pop('category'))
        except:
            raise serializers.ValidationError(response.make_messages([f'Категория {constants.RESPONSE_DOES_NOT_EXIST}']))

        application = Application.objects.create(**validated_data, category=category)

        documents = self.context.get('documents')
        doc_objects = []
        if documents:
            if len(documents) > 6:
                raise serializers.ValidationError(f'{constants.RESPONSE_MAX_FILES} 6')
            for doc in documents:
                doc_data = {
                    'application': application.id,
                    'document': doc
                    }
                serializer = ApplicationDocumentSerializer(data=doc_data)
                if serializer.is_valid():
                    doc_objects.append(serializer.save())
                else:
                    application.delete()
                    for doc_obj in doc_objects:
                        doc_obj.delete()
                    raise serializers.ValidationError(response.make_errors(serializer))
        return application


class PaidFeatureTypeListSerializer(serializers.ModelSerializer):
    time_unit = serializers.SerializerMethodField()

    class Meta:
        model = PaidFeatureType
        fields = ('id', 'time_amount', 'time_unit', 'text', 'price', 'beneficial')

    def get_time_unit(self, obj):
        return general.format_time_period(obj.time_amount, obj.time_unit)


class ProjectForPromotionSerialzier(serializers.Serializer):
    type = serializers.IntegerField(required=True)

    def validate_type(self, value):
        try:
            type = PaidFeatureType.objects.get(id=value)
        except:
            raise serializers.ValidationError(f'{constants.VALIDATION_FEATURE_NOT_EXIST} или яваляется Про продвижением')
        return value


class GetStatiscticsInSerialzier(serializers.Serializer):
    time_period = serializers.IntegerField(required=True)
    type = serializers.IntegerField(required=True)

    def validate_time_period(self, value):
        if value < 1 or value > len(constants.STATISTICS_TIME_PERIODS):
            raise serializers.ValidationError(constants.VALIDATION_TIME_PERIODS)
        return value

    def validate_type(self, value):
        if value < 1 or value > len(constants.STATISTICS_TYPES):
            raise serializers.ValidationError(constants.VALIDATION_STATISTICS_TYPES)
        return value


class GetStatiscticsOutSerialzier(serializers.ModelSerializer):
    project_id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    creation_date = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    to_profile_count = serializers.SerializerMethodField()
    to_favorites_count = serializers.SerializerMethodField()
    price = serializers.SerializerMethodField()
    is_top = serializers.SerializerMethodField()
    is_detailed = serializers.SerializerMethodField()

    class Meta:
        model = ProjectPaidFeature
        fields = ('id', 'project_id', 'name', 'creation_date', 'start_date', 'end_date', 'rating', 'to_profile_count',
                  'to_favorites_count', 'price', 'is_top', 'is_detailed')

    def get_project_id(self, obj):
        return obj.project.id

    def get_name(self, obj):
        return obj.project.name

    def get_creation_date(self, obj):
        return obj.project.creation_date.strftime(constants.DATE_FORMAT)

    def get_start_date(self, obj):
        return obj.created_at.strftime(constants.DATE_FORMAT)

    def get_end_date(self, obj):
        return obj.expires_at.strftime(constants.DATE_FORMAT)

    def get_rating(self, obj):
        return obj.project.rating

    def get_to_profile_count(self, obj):
        return obj.project.to_profile_count

    def get_to_favorites_count(self, obj):
        return ProjectUserFavorite.objects.filter(project=obj.project).count()

    def get_price(self, obj):
        return obj.type.price

    def get_is_top(self, obj):
        return obj.type.type == constants.PAID_FEATURE_TOP

    def get_is_detailed(self, obj):
        return obj.type.type == constants.PAID_FEATURE_DETAILED


class NotificationSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateTimeField(format=constants.DATETIME_FORMAT)

    class Meta:
        model = Notification
        fields = ('text', 'creation_date', 'read')



