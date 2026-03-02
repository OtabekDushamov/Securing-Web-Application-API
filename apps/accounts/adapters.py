"""
Custom django-allauth adapter so that after Google (or any social) login we redirect
to /accounts/complete/?next=... (or the stored next URL) instead of the 3rdparty signup page,
and so the user is sent straight back to checkauth.
"""
from django.conf import settings
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request, url=None, redirect_field_name="next", signup=False):
        # Prefer explicit next from request (GET or POST)
        redirect_to = request.GET.get(redirect_field_name) or request.POST.get(redirect_field_name)
        if not redirect_to and hasattr(request, "session"):
            # Allauth may not pass next through OAuth; we store it in middleware when starting Google login
            redirect_to = request.session.get(redirect_field_name) or request.session.pop("social_next", None)
        if redirect_to and self.is_safe_redirect_url(request, redirect_to):
            return redirect_to
        # Default: our complete page
        return reverse("accounts:complete")

    def is_safe_redirect_url(self, request, url):
        if not url:
            return False
        allowed_hosts = set(getattr(settings, "ALLOWED_HOSTS", []))
        if request.get_host():
            allowed_hosts.add(request.get_host())
        return url_has_allowed_host_and_scheme(url, allowed_hosts=allowed_hosts)

    def is_auto_signup(self, request, sociallogin):
        # Always auto-signup so we don't show the 3rdparty signup form
        return True

    def populate_user(self, request, sociallogin, data):
        """Ensure username is set from email if missing (our User model requires username)."""
        user = super().populate_user(request, sociallogin, data)
        if not user.username and user.email:
            base = user.email.split("@")[0].replace(".", "_")[:30]
            from django.contrib.auth import get_user_model
            User = get_user_model()
            name = base
            c = 0
            while User.objects.filter(username=name).exists():
                c += 1
                name = f"{base}{c}"[:30]
            user.username = name
        return user
