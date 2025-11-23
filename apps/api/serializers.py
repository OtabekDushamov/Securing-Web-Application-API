"""
Serializers for API endpoints.
"""
from rest_framework import serializers
from .models import Post, Comment
from apps.accounts.serializers import UserSerializer


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for Post model.
    """
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = Post
        fields = ('id', 'title', 'content', 'author', 'author_id', 'created_at', 'updated_at', 'is_published')
        read_only_fields = ('id', 'author', 'created_at', 'updated_at')
    
    def validate_title(self, value):
        """
        Validate title - prevent XSS by sanitizing input.
        """
        if len(value) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters long.")
        if len(value) > 200:
            raise serializers.ValidationError("Title must be less than 200 characters.")
        return value.strip()
    
    def validate_content(self, value):
        """
        Validate content - prevent injection attacks.
        """
        if len(value) < 10:
            raise serializers.ValidationError("Content must be at least 10 characters long.")
        return value.strip()
    
    def create(self, validated_data):
        """
        Create post with current user as author.
        """
        validated_data.pop('author_id', None)
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')
    
    def validate_content(self, value):
        """
        Validate content - prevent injection attacks.
        """
        if len(value) < 3:
            raise serializers.ValidationError("Comment must be at least 3 characters long.")
        if len(value) > 1000:
            raise serializers.ValidationError("Comment must be less than 1000 characters.")
        return value.strip()
    
    def create(self, validated_data):
        """
        Create comment with current user as author.
        """
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)

