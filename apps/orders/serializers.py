from rest_framework import serializers
from .models import Order, OrderItem
from apps.inventory.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price_at_time')
        read_only_fields = ('id', 'price_at_time')

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    # Write only field to accept products payload in POST request
    order_items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'total_amount', 'status', 'created_at', 'items', 'order_items')
        read_only_fields = ('id', 'user', 'total_amount', 'status', 'created_at')
