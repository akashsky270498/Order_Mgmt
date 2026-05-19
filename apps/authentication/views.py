from rest_framework import generics, permissions, status
from rest_framework.response import Response
from apps.users.models import User
from .serializers import UserSerializer, RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = UserSerializer(user).data
        # Note: The response automatically formats to the {status, msg, data, meta} 
        # structure because of our global CustomJSONRenderer
        return Response(
            {"msg": "User registered successfully.", "data": user_data},
            status=status.HTTP_201_CREATED
        )

class ProfileView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = UserSerializer
    
    def get_object(self):
        # Return the currently logged-in user
        return self.request.user
        
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "msg": "Profile fetched successfully.", 
            "data": serializer.data
        })
