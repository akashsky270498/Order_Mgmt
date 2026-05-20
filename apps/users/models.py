from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models
from common.models import BaseModel

class UserManager(DjangoUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if email is None:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        if username is None:
            username = email
        return super().create_user(username, email, password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        if email is None:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        if username is None:
            username = email
        return super().create_superuser(username, email, password, **extra_fields)

class User(AbstractUser, BaseModel):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('CUSTOMER', 'Customer'),
    )
    
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='CUSTOMER', db_index=True)
    
    objects = UserManager()
    
    # Authenticate using email instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['email', 'role']), # Compound index for faster auth & role checks
        ]
