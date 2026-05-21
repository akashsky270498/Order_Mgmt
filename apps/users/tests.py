from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase

from apps.users.models import User


class AdminUserManagementAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email='admin@test.com', password='password123', role='ADMIN')
        self.customer = User.objects.create_user(email='customer@test.com', password='password123', role='CUSTOMER')
        login_url = reverse('auth_login')
        admin_login = self.client.post(login_url, {'email': 'admin@test.com', 'password': 'password123'}, format='json')
        customer_login = self.client.post(login_url, {'email': 'customer@test.com', 'password': 'password123'}, format='json')
        self.admin_token = admin_login.data['access']
        self.customer_token = customer_login.data['access']

    def test_admin_can_list_customer_users(self):
        User.objects.create_user(email='another@test.com', password='password123', role='CUSTOMER')

        response = self.client.get(
            reverse('customer_user_list'),
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertTrue(all(user['role'] == 'CUSTOMER' for user in results))
        self.assertNotIn('admin@test.com', [user['email'] for user in results])

    def test_customer_cannot_list_users(self):
        response = self.client.get(
            reverse('customer_user_list'),
            HTTP_AUTHORIZATION=f'Bearer {self.customer_token}',
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_registration_always_creates_customer(self):
        response = self.client.post(
            reverse('auth_register'),
            {
                'email': 'new@test.com',
                'password': 'StrongPass123!',
                'first_name': 'New',
                'last_name': 'User',
                'role': 'ADMIN',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email='new@test.com').role, 'CUSTOMER')
