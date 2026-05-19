from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import BaseModel

class User(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CUSTOMER', 'Customer'),
    )
    
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CUSTOMER', db_index=True)
    
    # Authenticate using email instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email', 'role']), # Compound index for faster auth & role checks
        ]
