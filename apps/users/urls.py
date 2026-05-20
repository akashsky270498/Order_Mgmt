from django.urls import path

from .views import AdminUserDetailView, AdminUserListCreateView


urlpatterns = [
    path('', AdminUserListCreateView.as_view(), name='admin_user_list_create'),
    path('<uuid:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
]
