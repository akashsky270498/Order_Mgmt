from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Distributed Order Management System API",
      default_version='v1',
      description="API documentation for the microservices-inspired backend.",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth Service Endpoints
    path('api/auth/', include('apps.authentication.urls')),

    # Admin User Management Endpoints
    path('api/users/', include('apps.users.urls')),
    
    # Inventory Service Endpoints
    path('api/products/', include('apps.inventory.urls')),
    
    # Order Service Endpoints
    path('api/orders/', include('apps.orders.urls')),
    
    # Swagger Documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
