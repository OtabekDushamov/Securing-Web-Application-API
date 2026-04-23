"""
Frontend URL configuration for accounts app.
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('agreement/', views.agreement_page, name='agreement'),
    path('signup/', views.signup_redirect, name='signup_redirect'),
    path('logout/', views.logout_page, name='logout'),
    path('complete/', views.complete, name='complete'),
    path('profile/', views.profile_page, name='profile'),
]
