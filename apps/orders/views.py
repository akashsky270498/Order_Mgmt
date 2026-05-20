from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.db import transaction
from .models import Order, OrderItem
from apps.inventory.models import Product
from .serializers import OrderSerializer, OrderStatusUpdateSerializer
from apps.payments.tasks import process_payment
import logging

logger = logging.getLogger(__name__)

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Admins see all orders, customers see only their own
        if self.request.user.role == 'ADMIN':
            return Order.objects.all().order_by('-created_at')
        return Order.objects.filter(user=self.request.user).order_by('-created_at')
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        order_items_data = serializer.validated_data.pop('order_items', [])
        
        if not order_items_data:
            return Response({"msg": "Order must contain at least one item."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            with transaction.atomic(): # DB Atomicity: Rollback everything if any step fails
                # 1. Create Order (PENDING)
                order = Order.objects.create(user=request.user, status='PENDING')
                total_amount = 0
                
                # 2. Process Items and Inventory
                for item_data in order_items_data:
                    product_id = item_data.get('product')
                    quantity = item_data.get('quantity', 1)
                    
                    # select_for_update() locks the row until transaction finishes (prevents concurrent race conditions!)
                    product = Product.objects.select_for_update().get(id=product_id)
                    
                    if not product.is_active:
                        raise ValueError(f"Product {product.name} is not available.")
                        
                    if product.stock_quantity < quantity:
                        raise ValueError(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}")
                        
                    # Reserve Inventory
                    product.stock_quantity -= quantity
                    product.save()
                    
                    # Create OrderItem capturing the EXACT price right now
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price_at_time=product.price
                    )
                    
                    total_amount += (product.price * quantity)
                    
                # Update Order Total and Status
                order.total_amount = total_amount
                order.status = 'INVENTORY_RESERVED'
                order.save()
                
            # 3. Trigger Async Payment Task (outside the atomic block to ensure it runs only if DB commit succeeded)
            process_payment.delay(order.id)
            
            # 4. Return success to user immediately
            order_data = OrderSerializer(order).data
            return Response(
                {"msg": "Order placed successfully. Payment processing initiated asynchronously.", "data": order_data},
                status=status.HTTP_201_CREATED
            )
            
        except Product.DoesNotExist:
            return Response({"msg": "One or more products not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"msg": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error placing order for user {request.user.email}", exc_info=True)
            return Response({"msg": "An unexpected error occurred while placing order."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class OrderDetailView(generics.RetrieveUpdateAPIView):
    """
    GET: View single order details.
    PATCH: Admins can manually update status if needed.
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'ADMIN':
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

class OrderStatusUpdateView(generics.UpdateAPIView):
    """
    PATCH /api/orders/:id/status
    """
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        if request.user.role != 'ADMIN':
            return Response({"msg": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)
            
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        order_data = OrderSerializer(instance).data
        return Response({"msg": "Order status updated successfully.", "data": order_data})
