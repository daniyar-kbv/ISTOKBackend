from rest_framework import serializers

from users.models import MainUser, ClientProfile, MerchantProfile, MerchantPhone, CodeVerification

from utils import response

import constants

import re


class PhoneSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate_phone(self, value):
        regex = constants.PHONE_FORMAT
        if not isinstance(value, str) or re.search(regex, value) is None:
            raise serializers.ValidationError(constants.VALIDATION_PHONE_FORMAT_ERROR)
        return value


class UserClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainUser
        fields = ('email', 'password', 'role')


class ClientProfileCreateSerializer(serializers.ModelSerializer):
    user = UserClientCreateSerializer()

    class Meta:
        model = ClientProfile
        fields = ('first_name', 'last_name', 'date_of_birth', 'user')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = MainUser.objects.create_user(**user_data)
        profile = ClientProfile.objects.create(user=user, **validated_data)
        return profile


class MerchantProfileCreateSerializer(serializers.ModelSerializer):
    user = UserClientCreateSerializer()

    class Meta:
        model = MerchantProfile
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = MainUser.objects.create_user(**user_data)
        if self.context:
            for phone in self.context:
                serializer = PhoneSerializer(data={
                    'phone': phone
                })
                if serializer.is_valid():
                    try:
                        merchant_phone = MerchantPhone.objects.get(phone=phone)
                    except MerchantPhone.DoesNotExist:
                        user.delete()
                        raise serializers.ValidationError(constants.RESPONSE_VERIFICATION_DOES_NOT_EXIST)
                    if merchant_phone.user is not None:
                        user.delete()
                        raise serializers.ValidationError(f'{phone} {constants.RESPONSE_PHONE_REGISTERED}')
                    if not merchant_phone.is_valid:
                        user.delete()
                        raise serializers.ValidationError(constants.VALIDATION_PHONE_NOT_VERIFIED)
                    merchant_phone.user = user
                    merchant_phone.save()
                else:
                    user.delete()
                    raise serializers.ValidationError(response.make_errors(serializer))
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
        return profile


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    class Meta:
        model = MainUser
        fields = ('email', 'phone', 'password')

    def validate_email(self, value):
        if value == '' or value is None:
            raise serializers.ValidationError(constants.VALIDATION_CANT_BE_BLANK)
        return value

    def validate_phone(self, value):
        regex = constants.PHONE_FORMAT
        if not isinstance(value, str) or re.search(regex, value) is None:
            raise serializers.ValidationError(constants.VALIDATION_PHONE_FORMAT_ERROR)
        return value


class MerchantPhoneVerification(serializers.ModelSerializer):
    class Meta:
        model = MerchantPhone
        fields = '__all__'

    def validate_phone(self, value):
        regex = constants.PHONE_FORMAT
        if not isinstance(value, str) or re.search(regex, value) is None:
            raise serializers.ValidationError(constants.VALIDATION_PHONE_FORMAT_ERROR)
        return value


class CodeVerificationSerializer(serializers.ModelSerializer):
    phone = MerchantPhoneVerification()

    class Meta:
        model = CodeVerification
        fields = '__all__'

    def validate_code(self, value):
        for char in value:
            if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
                raise serializers.ValidationError(constants.VALIDATION_PHONE_FORMAT_ERROR)
        if len(value) != 4:
            raise serializers.ValidationError(constants.VALIDATION_PHONE_FORMAT_ERROR)
        return value

    def create(self, validated_data):
        phone = validated_data.pop('phone').get('phone')
        if MerchantPhone.objects.filter(phone=phone).count() > 0:
            try:
                merchant_phone = MerchantPhone.objects.get(phone=phone)
            except MerchantPhone.DoesNotExist:
                raise serializers.ValidationError(constants.RESPONSE_SERVER_ERROR)
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
