from django.db import models
from common.models import BaseModel
from apps.users.models import User
from apps.inventory.models import Product

class Order(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('INVENTORY_RESERVED', 'Inventory Reserved'),
        ('PAYMENT_PROCESSING', 'Payment Processing'),
        ('COMPLETED', 'Completed'),
        ('PAYMENT_FAILED', 'Payment Failed'),
        ('CANCELLED', 'Cancelled'),
        ('OUT_OF_STOCK', 'Out of Stock'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='PENDING', db_index=True)

    class Meta:
        db_table = 'orders'
        indexes = [
            models.Index(fields=['user', 'status']), # Very frequent query pattern (user looking at their orders)
            models.Index(fields=['created_at']), # Helpful for sorting and analytics
        ]

class OrderItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # PROTECT ensures we don't delete products that are part of an order history
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_items')
    quantity = models.PositiveIntegerField(default=1)
    # Store price at time of order since product prices can change! (Crucial for compliance)
    price_at_time = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'order_items'
        unique_together = ('order', 'product') # Prevent same product appearing as two separate lines
