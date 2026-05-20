from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Order

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    # Emit websocket event to notify frontend of status change
    channel_layer = get_channel_layer()
    room_group_name = f'order_{instance.user.id}'

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            'type': 'order_status_update',
            'order_id': str(instance.id),
            'status': instance.status
        }
    )
