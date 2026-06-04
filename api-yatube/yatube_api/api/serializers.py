from rest_framework import serializers

from posts.models import Comment, Group, Post


class GroupSerializers(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')


class CommentSerializer(serializers.ModelSerializer):
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
    comments = CommentSerializer(
        many=True,
        read_only=True
    )
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    group = serializers.SlugRelatedField(
        queryset=Group.objects.all(),
        slug_field='slug',
        required=False
    )

    class Meta:
        model = Post
        fields = (
            'id', 'text', 'author', 'image', 'pub_date', 'group', 'comments'
        )
