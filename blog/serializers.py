from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from blog.models import BlogPost, PostDocument
from users.serializers import UserShortSerializer


class BlogPostMainPageSerializer(serializers.ModelSerializer):
    user = UserShortSerializer()
    category_name = serializers.SerializerMethodField()
    city_name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ('id', 'user', 'category_name', 'city_name', 'title', 'photo')

    def get_category_name(self, obj):
        return obj.category.name

    def get_city_name(self, obj):
        return obj.city.name

    def get_photo(self, obj):
        photo = PostDocument.objects.filter(post=obj).first()
        if photo:
            return self.context.build_absolute_uri(photo.document.url)
        return None


class BlogPostSearchSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    user = UserShortSerializer()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ('id', 'user', 'photo', 'category_name', 'title', 'text', 'likes_count', 'is_liked')

    def get_photo(self, obj):
        photo = PostDocument.objects.filter(post=obj).first()
        if photo:
            return self.context.build_absolute_uri(photo.document.url)
        return None

    def get_user_id(self, obj):
        return obj.user.id

    def get_user_name(self, obj):
        return obj.user.get_full_name()

    def get_category_name(self, obj):
        return obj.category.name

    def get_likes_count(self, obj):
        return obj.user_likes.count()

    def get_is_liked(self, obj):
        user = self.context.user
        if not isinstance(user, AnonymousUser):
            if obj.user_likes.filter(id=user.id).count() > 0:
                return True
            else:
                return False
        return None
