from django.db import models
from .models import BaseModel
from django.conf import settings

class AuditLog(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    payload = models.TextField(blank=True) # Could be JSONField in Postgres/MySQL 8+

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
