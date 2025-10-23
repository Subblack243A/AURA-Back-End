from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import UserModel
from ..serializers import UserRegisterSerializer


class UserView(APIView):
    serializer_class = UserRegisterSerializer
    # Peticion POST creacion de nuevo usuario
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.create(validated_data=serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)