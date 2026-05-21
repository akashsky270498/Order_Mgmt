from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class CustomerUserSerializer(serializers.ModelSerializer):
    """Read-only customer data for admin user management"""
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'first_name',
            'last_name',
            'role',
            'is_active',
            'created_at',
            'updated_at',
        )
        read_only_fields = fields


class ToggleUserStatusSerializer(serializers.ModelSerializer):
    """Admin only - toggle user active/inactive status"""
    class Meta:
        model = User
        fields = ('id', 'email', 'is_active', 'first_name', 'last_name', 'role')
        read_only_fields = ('id', 'email', 'first_name', 'last_name', 'role')


class UpdateProfileSerializer(serializers.ModelSerializer):
    """User can update their own profile (name only, no email/role/password)"""
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'created_at')
        read_only_fields = ('id', 'email', 'role', 'created_at')

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Change password for authenticated users"""
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
