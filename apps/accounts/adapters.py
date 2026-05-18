"""
Custom django-allauth adapter so that after Google (or any social) login we redirect
to /accounts/complete/?next=... (or the stored next URL) instead of the 3rdparty signup page,
and so the user is sent straight back to checkauth.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_auto_signup_allowed(self, request, sociallogin):
        # Keep Google users out of the allauth 3rd-party signup form.
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
