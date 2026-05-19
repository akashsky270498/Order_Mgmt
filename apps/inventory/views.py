from rest_framework import generics, filters
from .models import Product
from .serializers import ProductSerializer
from common.permissions import IsAdminOrReadOnly

class ProductListCreateView(generics.ListCreateAPIView):
    """
    GET: List all products (Customers & Admins)
    POST: Create a new product (Admins only)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve product details (Customers & Admins)
    PATCH/PUT: Update product (Admins only)
    DELETE: Delete product (Admins only)
    """
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
