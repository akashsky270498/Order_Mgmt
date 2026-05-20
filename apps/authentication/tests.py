from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from apps.users.models import User

class AuthenticationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('auth_login')
        self.logout_url = reverse('auth_logout')
        self.profile_url = reverse('auth_profile')

    def test_login_missing_email(self):
        response = self.client.post(
            self.login_url,
            {'username': 'admin@test.com', 'password': 'password123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'email': 'nonexistent@test.com', 'password': 'wrongpassword'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_and_profile_with_prefixless_token(self):
        User.objects.create_user(email='testuser@test.com', password='password123')
        response = self.client.post(
            self.login_url,
            {'email': 'testuser@test.com', 'password': 'password123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['access']
        response = self.client.get(
            self.profile_url,
            HTTP_AUTHORIZATION=token,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], 'testuser@test.com')

    def test_logout_blacklists_refresh_token(self):
        User.objects.create_user(email='logout@test.com', password='password123')
        response = self.client.post(
            self.login_url,
            {'email': 'logout@test.com', 'password': 'password123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        access = response.data['access']
        refresh = response.data['refresh']
        logout_response = self.client.post(
            self.logout_url,
            {'refresh': refresh},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {access}'
        )
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

        refresh_response = self.client.post(
            reverse('auth_refresh'),
            {'refresh': refresh},
            format='json'
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
