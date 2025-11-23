"""
Views for API endpoints.
Demonstrates security features like authentication, rate limiting, and input validation.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework import filters
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
try:
    from django_filters.rest_framework import DjangoFilterBackend
except ImportError:
    DjangoFilterBackend = None
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer


# Frontend Views
@login_required
def dashboard_page(request):
    """Render dashboard page"""
    return render(request, 'api/dashboard.html')


@login_required
def posts_page(request):
    """Render posts management page"""
    return render(request, 'api/posts.html')


# API Views
class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post model.
    Demonstrates CRUD operations with authentication and permissions.
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    # Configure filter backends
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    if DjangoFilterBackend:
        filter_backends.insert(0, DjangoFilterBackend)
    
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Filter posts based on user permissions and query parameters.
        Users can only see their own posts or published posts.
        """
        user = self.request.user
        
        # Base filtering by user permissions
        if user.is_staff:
            queryset = Post.objects.all()
        else:
            queryset = Post.objects.filter(author=user) | Post.objects.filter(is_published=True)
        
        # Apply additional filters from query parameters
        is_published = self.request.query_params.get('is_published', None)
        author_id = self.request.query_params.get('author', None)
        
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() == 'true')
        if author_id is not None:
            queryset = queryset.filter(author_id=author_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set the author to the current user.
        """
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        """
        Publish a post (only author can publish).
        POST /api/posts/{id}/publish/
        """
        post = self.get_object()
        if post.author != request.user:
            return Response(
                {'error': 'You do not have permission to publish this post.'},
                status=status.HTTP_403_FORBIDDEN
            )
        post.is_published = True
        post.save()
        return Response({'message': 'Post published successfully'})


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment model.
    Demonstrates nested resources with authentication.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    
    def get_queryset(self):
        """
        Filter comments by post if post_id is provided.
        """
        queryset = Comment.objects.all()
        post_id = self.request.query_params.get('post_id', None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)
        return queryset
    
    def perform_create(self, serializer):
        """
        Set the author to the current user.
        """
        serializer.save(author=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def public_posts(request):
    """
    Public endpoint for published posts.
    GET /api/public/posts/
    Demonstrates rate limiting for anonymous users.
    """
    throttle_classes = [AnonRateThrottle]
    posts = Post.objects.filter(is_published=True).order_by('-created_at')
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    User statistics endpoint.
    GET /api/stats/
    Demonstrates authenticated endpoint with user-specific data.
    """
    user = request.user
    stats = {
        'username': user.username,
        'total_posts': Post.objects.filter(author=user).count(),
        'published_posts': Post.objects.filter(author=user, is_published=True).count(),
        'total_comments': Comment.objects.filter(author=user).count(),
    }
    return Response(stats)
