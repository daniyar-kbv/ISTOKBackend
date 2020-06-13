from rest_framework import serializers
from users.models import MainUser, ClientProfile
from users.serializers import PhoneSerializer, MerchantPhone
from profiles.models import FormAnswer, FormQuestion, FormQuestionGroup, FormUserAnswer
from utils import response, upload, validators
import constants


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


class FormAnswerPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAnswer
        fields = ('id', )
