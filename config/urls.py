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
    # Our login/register/complete take precedence; allauth handles /accounts/google/login/ etc.
    path('accounts/', include('apps.accounts.urls')),
    path('accounts/', include('allauth.urls')),
    
    # Root redirect: if authenticated go to complete (handles next/source) or dashboard; else login
    path('', lambda request: redirect('accounts:complete') if request.user.is_authenticated else redirect('accounts:login'), name='home'),
    
    # JWT Token endpoints
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Frontend pages (dashboard, posts)
    path('', include('apps.api.urls')),
    
    # API endpoints  
    path('api/accounts/', include('apps.accounts.api_urls')),
    path('api/', include('apps.api.api_urls')),
]
