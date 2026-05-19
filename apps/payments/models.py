from django.db import models
from common.models import BaseModel
from apps.orders.models import Order
import uuid

class Payment(BaseModel):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )
    
    # 1:1 relation as each order has one payment attempt tracking record (in a real system it might be 1:N for retries)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    # Indexed for idempotency / third-party callbacks
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4, db_index=True) 
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'payments'
