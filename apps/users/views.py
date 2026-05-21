from rest_framework import filters, generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdminRole
from .models import User
from .serializers import (
    CustomerUserSerializer,
    ToggleUserStatusSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
)


class CustomerUserListView(generics.ListAPIView):
    """Admin only - list customer users"""
    serializer_class = CustomerUserSerializer
    permission_classes = [IsAdminRole]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'email']

    def get_queryset(self):
        return User.objects.filter(role='CUSTOMER').order_by('-created_at')


class ToggleUserStatusView(APIView):
    """Admin only - toggle user active/inactive status"""
    permission_classes = [IsAdminRole]

    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"msg": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Toggle is_active status
        user.is_active = not user.is_active
        user.save()

        serializer = ToggleUserStatusSerializer(user)
        return Response(
            {
                "msg": f"User {'activated' if user.is_active else 'deactivated'} successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class UpdateProfileView(generics.UpdateAPIView):
    """User can update their own profile (name only)"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {
                "msg": "Profile updated successfully.",
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    """Change password for authenticated users"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response(
            {"msg": "Password changed successfully."},
            status=status.HTTP_200_OK
        )
