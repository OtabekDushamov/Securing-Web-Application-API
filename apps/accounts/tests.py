from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from allauth.account.models import EmailAddress
from allauth.core import context as allauth_context
from allauth.socialaccount.models import SocialAccount, SocialLogin
from rest_framework.test import APIClient


User = get_user_model()


class RegistrationSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_api_registration_requires_agreement(self):
        response = self.client.post(reverse('accounts-api:register'), {
            'username': 'apiuser',
            'email': 'apiuser@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('accepted_user_agreement', response.data['error']['details'])

    def test_api_registration_rejects_weak_password(self):
        response = self.client.post(reverse('accounts-api:register'), {
            'username': 'weakapi',
            'email': 'weakapi@example.com',
            'password': 'weakpass',
            'password_confirm': 'weakpass',
            'accepted_user_agreement': True,
        }, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data['error']['details'])

    def test_web_registration_stores_agreement_acceptance(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'webuser',
            'email': 'webuser@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'accepted_user_agreement': 'on',
        })

        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='webuser')
        self.assertTrue(user.accepted_user_agreement)
        self.assertIsNotNone(user.user_agreement_accepted_at)

    def test_web_registration_rejects_missing_agreement(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'nouseragreement',
            'email': 'nouseragreement@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username='nouseragreement').exists())


class GoogleAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_page_google_link_returns_to_complete_with_original_next(self):
        external_next = 'https://checkauth.otabekdushamov.uz/'

        response = self.client.get(
            reverse('accounts:login'),
            {'next': external_next},
            HTTP_HOST='auth.otabekdushamov.uz',
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn(reverse('google_login'), content)
        self.assertIn('auth.otabekdushamov.uz/accounts/complete/', content)
        self.assertIn('checkauth.otabekdushamov.uz', content)

    def test_google_login_get_starts_oauth_redirect(self):
        response = self.client.get(
            reverse('google_login'),
            {'next': reverse('accounts:complete')},
            HTTP_HOST='auth.otabekdushamov.uz',
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response['Location'].startswith('https://accounts.google.com/')
        )

    def test_google_verified_email_matches_existing_local_user(self):
        existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='StrongPass123!',
        )
        sociallogin = SocialLogin(
            user=User(username='googleuser', email='existing@example.com'),
            account=SocialAccount(provider='google', uid='google-123'),
            email_addresses=[
                EmailAddress(email='existing@example.com', verified=True, primary=True),
            ],
        )
        request = RequestFactory().get(
            '/accounts/google/login/callback/',
            HTTP_HOST='auth.otabekdushamov.uz',
        )

        with allauth_context.request_context(request):
            sociallogin.lookup()

        self.assertEqual(sociallogin.user.pk, existing_user.pk)
