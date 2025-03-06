from rest_framework import serializers
from api.models.blog_models import BlogPost, BlogPostLike, BlogPostComment


class BlogPostSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'author', 'author_username', 'description', 'classe', 'image', 'created_at', 'likes_count', 'comments_count']
        read_only_fields = ['author', 'created_at']


class BlogPostCommentSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = BlogPostComment
        fields = ['id', 'user', 'user_username', 'post', 'content', 'created_at']
        read_only_fields = ['user', 'post', 'created_at']


class BlogPostLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPostLike
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'post', 'created_at']
