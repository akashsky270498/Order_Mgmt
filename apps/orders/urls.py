from django.urls import path
from .views import OrderListCreateView, OrderDetailView, OrderStatusUpdateView

urlpatterns = [
    path('', OrderListCreateView.as_view(), name='order_list_create'),
    path('<uuid:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('<uuid:pk>/status/', OrderStatusUpdateView.as_view(), name='order_status_update'),
]
