from django.urls import reverse
from rest_framework import serializers
from payments.models import PaidFeatureType, ProjectLinkedPaidFeatures
from utils import general
import constants, requests


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


class PaidFeaturePostSerializer(serializers.Serializer):
    type = serializers.IntegerField(required=True)
    target = serializers.IntegerField(required=True)
    token = serializers.CharField(required=True)
    packet = serializers.CharField(required=True)

    def validate(self, data):
        type = data['type']
        target = data['target']
        token = data['token']
        if target > len(constants.PAID_FEATURE_FOR_TYPES):
            raise serializers.ValidationError(constants.VALIDATION_TARGET_INVALID)
        try:
            feature = PaidFeatureType.objects.get(id=type)
        except:
            raise serializers.ValidationError(
                f'{constants.VALIDATION_FEATURE_NOT_EXIST}')
        if target == constants.PAID_FEATURE_FOR_USER and feature.type != constants.PAID_FEATURE_PRO:
            raise serializers.ValidationError(
                constants.VALIDATION_FEATURE_TYPE_NOT_FOR.format(
                    'пользователя',
                    constants.PAID_FEATURE_PRO
                )
            )
        if target == constants.PAID_FEATURE_FOR_PROJECT and feature.type == constants.PAID_FEATURE_PRO:
            raise serializers.ValidationError(
                constants.VALIDATION_FEATURE_TYPE_NOT_FOR.format(
                    'пользователя',
                    ', '.join([f'{x[0]}' for x in constants.PAID_FEATURE_TYPES if x[0] != constants.PAID_FEATURE_PRO])
                )
            )
        if feature.type == constants.PAID_FEATURE_TOP_DETAILED:
            try:
                ProjectLinkedPaidFeatures.objects.get(main_feature=feature)
            except:
                raise serializers.ValidationError(constants)
        auth_response = requests.get(self.context, headers={
            'Authorization': f'JWT {token}'
        })
        if auth_response.status_code != 200:
            raise serializers.ValidationError(constants.VALIDATION_TOKEN_INVALID)
        return data
