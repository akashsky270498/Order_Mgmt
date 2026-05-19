from django.db import models
import uuid

class BaseModel(models.Model):
    """
    Abstract Base Model providing UUID primary key, 
    and automatic creation/update timestamps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
