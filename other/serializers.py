from rest_framework import serializers
from other.models import FAQ


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = '__all__'
