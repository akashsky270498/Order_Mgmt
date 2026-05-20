from rest_framework import serializers
from .models import Order, OrderItem
from apps.inventory.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_name', 'quantity', 'price_at_time')
        read_only_fields = ('id', 'price_at_time')

class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items in POST request"""
    product = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(required=True, min_value=1)

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    # Write only field to accept products payload in POST request
    order_items = OrderItemCreateSerializer(many=True, write_only=True, required=True)
    
    class Meta:
        model = Order
        fields = ('id', 'user', 'total_amount', 'status', 'created_at', 'items', 'order_items')
        read_only_fields = ('id', 'user', 'total_amount', 'status', 'created_at')

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating order status (PATCH)"""
    class Meta:
        model = Order
        fields = ('status',)
        
    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return value
