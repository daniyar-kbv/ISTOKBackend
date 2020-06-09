from rest_framework import serializers
from users.models import MainUser
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
        return obj.profile.phone

    def get_date_of_birth(self, obj):
        return obj.profile.date_of_birth

    def get_rating(self, obj):
        return obj.profile.rating
