from celery import shared_task
from django.db import transaction
import time
import random
from apps.orders.models import Order
from apps.payments.models import Payment
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_payment(order_id):
    """
    Simulates asynchronous payment processing.
    """
    try:
        order = Order.objects.get(id=order_id)
        
        # Simulate Network Delay (Payment Gateway)
        time.sleep(3) 
        
        with transaction.atomic():
            # Create a pending payment record
            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                status='PENDING'
            )
            
            # Simulate Success/Failure (80% success rate)
            success = random.random() < 0.8
            
            if success:
                payment.status = 'SUCCESS'
                order.status = 'COMPLETED'
            else:
                payment.status = 'FAILED'
                payment.error_message = 'Insufficient funds or gateway timeout'
                order.status = 'FAILED'
                
                # Payment Failed -> Rollback reserved inventory!
                for item in order.items.select_for_update():
                    item.product.stock_quantity += item.quantity
                    item.product.save()
                    
            payment.save()
            order.save()
            
    except Order.DoesNotExist:
        logger.warning(f"Order {order_id} does not exist during payment processing.")
    except Exception as e:
        logger.error(f"Error processing payment for order {order_id}", exc_info=True)
        # In a real system, self.retry(exc=e) would be used here.
