"""
Views for user authentication and management.
"""
import json
import base64
from urllib.parse import urlencode

from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate, login
from django.utils import timezone
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer

User = get_user_model()


def _user_data_json(user):
    """Return dict of user data for JSON response (no sensitive fields)."""
    return UserSerializer(user).data


def _redirect_to_source_with_user_data(redirect_url, user):
    """Redirect to external URL with user data in fragment (#data=base64url)."""
    data = _user_data_json(user)
    payload = json.dumps(data, default=str)
    encoded = base64.urlsafe_b64encode(payload.encode()).decode().rstrip('=')
    fragment = f'data={encoded}'
    if '#' in redirect_url:
        base_url, existing = redirect_url.split('#', 1)
        fragment = f'{existing}&{fragment}' if existing else fragment
        return redirect(f'{base_url}#{fragment}')
    return redirect(f'{redirect_url}#{fragment}')


# Frontend Views
@require_http_methods(['GET', 'POST'])
@csrf_protect
def login_page(request):
    """Render login page or handle session login; pass next/source for redirect after auth."""
    if request.user.is_authenticated:
        next_url = (request.GET.get('next') or request.GET.get('source') or '').strip()
        if next_url:
            return redirect(reverse('accounts:complete') + '?' + urlencode({'next': next_url}))
        return redirect('accounts:complete')
    next_val = (request.GET.get('next') or request.GET.get('source') or '').strip()
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is None:
            messages.error(request, 'Invalid username or password.')
            return redirect(reverse('accounts:login') + ('?' + urlencode({'next': next_val}) if next_val else ''))
        if not user.is_active:
            messages.error(request, 'Account is disabled.')
            return redirect('accounts:login')
        login(request, user)
        user.last_login = timezone.now()
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save()
        return redirect(reverse('accounts:complete') + ('?' + urlencode({'next': next_val}) if next_val else ''))
    return render(request, 'accounts/login.html', {'next_url': next_val})


@require_http_methods(['GET', 'POST'])
@csrf_protect
def register_page(request):
    """Render register page or handle session registration; pass next/source for redirect after auth."""
    if request.user.is_authenticated:
        next_url = (request.GET.get('next') or request.GET.get('source') or '').strip()
        if next_url:
            return redirect(reverse('accounts:complete') + '?' + urlencode({'next': next_url}))
        return redirect('accounts:complete')
    next_val = request.GET.get('next') or request.GET.get('source') or ''
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        if password != password_confirm:
            messages.error(request, "Passwords don't match.")
            return redirect(reverse('accounts:register') + ('?' + urlencode({'next': next_val}) if next_val else ''))
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return redirect(reverse('accounts:register') + ('?' + urlencode({'next': next_val}) if next_val else ''))
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect(reverse('accounts:register') + ('?' + urlencode({'next': next_val}) if next_val else ''))
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
        except Exception as e:
            messages.error(request, str(e) or 'Registration failed.')
            return redirect('accounts:register')
        login(request, user)
        return redirect(reverse('accounts:complete') + ('?' + urlencode({'next': next_val}) if next_val else ''))
    return render(request, 'accounts/register.html', {'next_url': next_val})


@login_required(login_url='/accounts/login/')
def complete(request):
    """
    After login/register: if next/source provided, redirect there with user data in fragment.
    Otherwise show the user-data page (JSON).
    """
    next_url = request.GET.get('next') or request.GET.get('source', '').strip()
    if next_url:
        return _redirect_to_source_with_user_data(next_url, request.user)
    return render(request, 'accounts/user_data.html', {
        'user_data': json.dumps(_user_data_json(request.user), indent=2, default=str),
    })


@login_required
def profile_page(request):
    """Render profile page"""
    return render(request, 'accounts/profile.html')


# API Views
class RegisterView(generics.CreateAPIView):
    """
    User registration endpoint.
    POST /api/accounts/register/
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User registered successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint.
    POST /api/accounts/login/
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    
    # Update last login
    user.last_login = timezone.now()
    user.last_login_ip = request.META.get('REMOTE_ADDR')
    user.save()
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    
    return Response({
        'message': 'Login successful',
        'user': UserSerializer(user).data,
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint.
    GET /api/accounts/profile/ - Get current user profile
    PUT /api/accounts/profile/ - Update current user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint.
    POST /api/accounts/logout/
    Blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Refresh token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )
