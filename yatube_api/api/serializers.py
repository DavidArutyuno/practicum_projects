from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField


from posts.models import Comment, Follow, Group, Post


User = get_user_model()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализация данных модели Follow."""
    user = SlugRelatedField(
        slug_field='username',
        read_only=True,
    )
    following = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        read_only=False,
        required=True,
    )

    class Meta:
        model = Follow
        fields = ('id', 'user', 'following', )

    def validate_following(self, following):
        user = self.context.get('request').user
        if user == following:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя!'
            )
        if Follow.objects.filter(user=user, following=following).exists():
            raise serializers.ValidationError(
                'Уже подписаны на этого пользователя!'
            )
        return following


class GroupSerializers(serializers.ModelSerializer):
    """Сериализация данных модели Group."""

    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализация данных модели Comment."""
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')


class PostSerializer(serializers.ModelSerializer):
    """Сериализация данных модели Post."""
    comments = CommentSerializer(
        many=True,
        read_only=True,
        required=False
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'author', 'image', 'pub_date', 'group', 'comments'
        )
