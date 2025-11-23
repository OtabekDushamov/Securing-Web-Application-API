"""
Models for the API app.
Demo models to showcase security features.
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    """
    Demo Post model for API endpoints.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Demo Comment model for API endpoints.
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
