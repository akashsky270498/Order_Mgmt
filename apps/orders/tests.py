from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from apps.users.models import User
from apps.inventory.models import Product
from apps.orders.models import Order

class OrderAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email='customer@test.com', password='password123', role='CUSTOMER')
        self.admin = User.objects.create_user(email='admin@test.com', password='password123', role='ADMIN')
        self.product = Product.objects.create(name='Test Product', price=100.00, stock_quantity=10, is_active=True)
        login_url = reverse('auth_login')
        response = self.client.post(login_url, {'email': 'customer@test.com', 'password': 'password123'}, format='json')
        self.customer_token = response.data['access']

    def test_place_order_success(self):
        response = self.client.post(
            reverse('order_list_create'),
            {'order_items': [{'product': str(self.product.id), 'quantity': 2}]},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.customer_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, 8)

    def test_place_order_insufficient_stock(self):
        response = self.client.post(
            reverse('order_list_create'),
            {'order_items': [{'product': str(self.product.id), 'quantity': 20}]},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.customer_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Insufficient stock', response.data['msg'])
        self.assertEqual(Order.objects.count(), 0)
