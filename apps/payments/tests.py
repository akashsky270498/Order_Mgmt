from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from apps.users.models import User
from apps.inventory.models import Product
from apps.orders.models import Order

class PaymentTaskTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = User.objects.create_user(email='customer2@test.com', password='password123', role='CUSTOMER')
        login_url = reverse('auth_login')
        response = self.client.post(login_url, {'email': 'customer2@test.com', 'password': 'password123'}, format='json')
        self.customer_token = response.data['access']
        self.product = Product.objects.create(name='Payment Product', price=15.00, stock_quantity=5, is_active=True)

    def test_order_triggers_payment_task(self):
        response = self.client.post(
            reverse('order_list_create'),
            {'order_items': [{'product': str(self.product.id), 'quantity': 1}]},
            format='json',
            HTTP_AUTHORIZATION=f'Bearer {self.customer_token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.status, 'INVENTORY_RESERVED')
