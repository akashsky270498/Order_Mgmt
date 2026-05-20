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

    def test_admin_can_create_user_with_role(self):
        response = self.client.post(
            reverse('admin_user_list_create'),
            {
                'email': 'manager@test.com',
                'password': 'StrongPass123!',
                'first_name': 'Ops',
                'last_name': 'Manager',
                'role': 'ADMIN',
                'is_active': True,
            },
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.get(email='manager@test.com').role, 'ADMIN')

    def test_customer_cannot_manage_users(self):
        response = self.client.get(
            reverse('admin_user_list_create'),
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
