from django.db import models
from common.models import BaseModel
from django.core.validators import MinValueValidator
from decimal import Decimal

class Product(BaseModel):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    # Keeping stock normalized. Prevent negative stock at DB level via check constraints if DB supports it, 
    # but MinValueValidator handles it at the ORM level.
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = 'products'
        indexes = [
            models.Index(fields=['is_active', 'name']), # Index for optimized searching of active products
        ]
