from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import UserModel
from ..serializers import UserRegisterSerializer

class UserView(APIView):
    
    # Peticion POST creacion de nuevo usuario
    def post(self, request, format=None):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.create()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Peticion GET de usuario u
    def get(self, request, format=None):
        users = UserModel.objects.all()
        serializer = UserRegisterSerializer(users, many=True)
        return Response(serializer.data)