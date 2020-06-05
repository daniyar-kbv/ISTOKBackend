from django.contrib.auth.models import AnonymousUser
from rest_framework import serializers
from blog.models import BlogPost, PostDocument
from users.serializers import UserShortSerializer, UserShortAvatarSerializer


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


class BlogPostSideBarSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ('id', 'title', 'photo')

    def get_photo(self, obj):
        photo = PostDocument.objects.filter(post=obj).first()
        if photo:
            return self.context.build_absolute_uri(photo.document.url)
        return None


class BlogPostDetailSerializer(serializers.ModelSerializer):
    user = UserShortAvatarSerializer()
    category_name = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    photos = serializers.SerializerMethodField()
    liked_posts = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ('id', 'user', 'category_name', 'title', 'subtitle', 'likes_count', 'is_liked', 'photos', 'text',
                  'liked_posts')

    def get_photos(self, obj):
        urls = []
        photos = PostDocument.objects.filter(post=obj)
        for photo in photos:
            urls.append(self.context.build_absolute_uri(photo.document.url))
        return urls

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

    def get_liked_posts(self, obj):
        posts = []
        users = obj.user_likes.all()
        for user in users:
            user_posts = user.blog_post_likes.all()
            for post in user_posts:
                if post != obj:
                    posts.append(post)
        serializer = BlogPostSideBarSerializer(posts, many=True, context=self.context)
        return serializer.data
