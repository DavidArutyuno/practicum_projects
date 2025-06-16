from rest_framework import serializers

from posts.models import Comment, Group, Post


class GroupSerializers(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'title', 'slug', 'description')


# class PostSerializer(serializers.ModelSerializer):
#     author = serializers.StringRelatedField(
#         read_only=True,
#         default=serializers.CurrentUserDefault()
#     )
#     group = serializers.SlugRelatedField(
#         queryset=Group.objects.all(),
#         slug_field='slug',
#         required=False
#     )

#     class Meta:
#         model = Post
#         fields = ('id', 'text', 'author', 'image', 'pub_date', 'group')


# class CommentSerializer(serializers.ModelSerializer):
#     author = serializers.StringRelatedField(
#         read_only=True,
#         default=serializers.CurrentUserDefault()
#     )
#     post = serializers.PrimaryKeyRelatedField(
#         read_only=True
#     )

#     class Meta:
#         model = Comment
#         fields = ('id', 'author', 'post', 'text', 'created')


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'author', 'post', 'text', 'created')
        # read_only_fields = ['author', 'post']


class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(
        many=True,
        read_only=True
    )
    author = serializers.StringRelatedField(
        read_only=True,
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
        read_only_fields = ['comments', 'author', 'post']
