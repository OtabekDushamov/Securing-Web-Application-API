"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Root redirect to dashboard (or login if not authenticated)
    path('', lambda request: redirect('dashboard') if request.user.is_authenticated else redirect('login'), name='home'),
    
    # JWT Token endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Frontend pages
    path('accounts/', include('apps.accounts.urls')),
    path('', include('apps.api.urls')),
    
    # API endpoints  
    path('api/accounts/', include('apps.accounts.api_urls')),
    path('api/', include('apps.api.api_urls')),
]
