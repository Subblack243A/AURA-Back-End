from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from ..serializers import UserLoginSerializer


class UserLoginView(APIView):
    # Vista para login de Usuarios, no se rquiere autentificacion
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = UserLoginSerializer
    
    def post(self, request, *args, **kwargs):
        
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            # Buscar el username en la base de datos haciendo uso del email
            UserModel = get_user_model()
            try:
                user_obj = UserModel.objects.get(email=email)
            except:
                return Response(
                    {'error': 'Credenciales erroneas'}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            username = user_obj.username
            
            # Se hace autenticacion y se genera token
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        'token': token.key,
                        'user_id': user.pk,
                        'username': user.username
                    },
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'error': 'Credenciales erroneas'
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )