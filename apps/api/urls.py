"""
Frontend URL configuration for API app.
"""
from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('posts/', views.posts_page, name='posts'),
]

