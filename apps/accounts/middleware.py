"""
Middleware to store the 'next' parameter in session when user starts Google (social) login.
After OAuth callback, the adapter can read it and redirect to complete?next=checkauth.
"""


class SocialLoginNextMiddleware:
    """Store next= in session when visiting /accounts/google/login/?next=... so redirect survives OAuth."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.rstrip("/") == "/accounts/google/login" and request.GET.get("next"):
            request.session["social_next"] = request.GET.get("next")
        return self.get_response(request)
