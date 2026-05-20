import pytest
from django.urls import reverse
from rest_framework import status
from apps.users.models import User
from apps.inventory.models import Product
from apps.orders.models import Order

@pytest.mark.django_db
class TestOrderAPI:
    def setup_method(self):
        self.customer = User.objects.create_user(email='customer@test.com', password='password123', role='CUSTOMER')
        self.admin = User.objects.create_user(email='admin@test.com', password='password123', role='ADMIN')
        self.product = Product.objects.create(name='Test Product', price=100.00, stock_quantity=10, is_active=True)

    def test_place_order_success(self, client):
        client.force_login(self.customer)
        # Using DRF client or standard client, we need to authenticate properly.
        # Since we use simplejwt, let's just get the token
        response = client.post(reverse('auth_login'), {'email': 'customer@test.com', 'password': 'password123'}, content_type='application/json')
        token = response.data['access']
        
        response = client.post(
            reverse('order_list_create'),
            {
                'order_items': [{'product': str(self.product.id), 'quantity': 2}]
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.count() == 1
        
        # Verify inventory was reduced
        self.product.refresh_from_db()
        assert self.product.stock_quantity == 8
        
    def test_place_order_insufficient_stock(self, client):
        response = client.post(reverse('auth_login'), {'email': 'customer@test.com', 'password': 'password123'}, content_type='application/json')
        token = response.data['access']
        
        response = client.post(
            reverse('order_list_create'),
            {
                'order_items': [{'product': str(self.product.id), 'quantity': 20}] # Requesting more than stock
            },
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        print("Status code:", response.status_code)
        print("Data:", response.data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'Insufficient stock' in response.data['msg']
        assert Order.objects.count() == 0
