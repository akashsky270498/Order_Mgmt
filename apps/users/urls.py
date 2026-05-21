from django.urls import path

from .views import (
    CustomerUserListView,
    ToggleUserStatusView,
    UpdateProfileView,
    ChangePasswordView,
)

urlpatterns = [
    # Admin - list customer users
    path('', CustomerUserListView.as_view(), name='customer_user_list'),

    # Admin - toggle user status
    path('<uuid:user_id>/toggle-status/', ToggleUserStatusView.as_view(), name='toggle_user_status'),
    
    # User profile management
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change_password'),
]
