from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
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
