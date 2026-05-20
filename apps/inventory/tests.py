from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from apps.users.models import User
from apps.inventory.models import Product

class InventoryAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(email='admin@test.com', password='password123', role='ADMIN')
        self.product = Product.objects.create(name='Inventory Test', price=10.00, stock_quantity=5, is_active=True)
        login_url = reverse('auth_login')
        response = self.client.post(login_url, {'email': 'admin@test.com', 'password': 'password123'}, format='json')
        self.admin_token = response.data['access']

    def test_anonymous_user_cannot_list_products(self):
        response = self.client.get(reverse('product_list_create'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_can_create_product(self):
        response = self.client.post(
            reverse('product_list_create'),
            {'name': 'New Product', 'description': 'Test', 'price': 20.00, 'stock_quantity': 10, 'is_active': True},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.filter(name='New Product').count(), 1)
