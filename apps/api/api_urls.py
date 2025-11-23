"""
API URL configuration for API app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'posts', views.PostViewSet, basename='post')
router.register(r'comments', views.CommentViewSet, basename='comment')

app_name = 'api-endpoints'

urlpatterns = [
    path('', include(router.urls)),
    path('public/posts/', views.public_posts, name='public-posts'),
    path('stats/', views.user_stats, name='user-stats'),
]

