import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User

@pytest.mark.django_db
class TestAuthenticationAPI:
    def test_login_missing_email(self, client):
        url = reverse('auth_login')
        data = {
            'username': 'admin@test.com',
            'password': 'password123'
        }
        response = client.post(url, data, content_type='application/json')
        print("Missing email status:", response.status_code)
        print("Missing email data:", response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_invalid_credentials(self, client):
        url = reverse('auth_login')
        data = {
            'email': 'nonexistent@test.com',
            'password': 'wrongpassword'
        }
        response = client.post(url, data, content_type='application/json')
        print("Invalid creds status:", response.status_code)
        print("Invalid creds data:", response.data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_and_profile_with_prefixless_token(self, client):
        # Create user
        user = User.objects.create_user(email='testuser@test.com', password='password123')
        
        # Log in
        url = reverse('auth_login')
        data = {
            'email': 'testuser@test.com',
            'password': 'password123'
        }
        response = client.post(url, data, content_type='application/json')
        token = response.data['access']
        
        # Access profile without Bearer prefix
        profile_url = reverse('auth_profile')
        response = client.get(
            profile_url,
            HTTP_AUTHORIZATION=token  # Just raw token
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['email'] == 'testuser@test.com'

