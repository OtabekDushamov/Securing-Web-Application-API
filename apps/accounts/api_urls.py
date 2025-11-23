"""
API URL configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts-api'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
]

