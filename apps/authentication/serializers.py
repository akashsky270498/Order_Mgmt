from rest_framework import serializers
from apps.users.models import User
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'created_at')
        read_only_fields = ('id', 'role', 'created_at')

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name')
        
    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['email'], # Django requirement for AbstractUser
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='CUSTOMER' # Everyone registers as customer by default
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
