from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.contrib.auth import authenticate, get_user_model
from rest_framework.authtoken.models import Token
from ..serializers import UserLoginSerializer
from ..services.deepface_service import DeepFaceService
from ..models.tables.recognition_model import RecognitionModel
from rest_framework.exceptions import ValidationError


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
            
            # Se hace autenticacion
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # 1. Verificar si el usuario tiene registro facial (embedding)
                if not user.Face:
                    return Response(
                        {
                            'error': 'Face registration required',
                            'code': 'FACE_REGISTRATION_REQUIRED'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

                # 2. Verificar si se envió la imagen para análisis de emociones
                if 'image' not in request.FILES:
                    return Response(
                        {'error': 'Image file is required for emotion analysis'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                try:
                    # 3. Procesar imagen y analizar emociones
                    image_file = request.FILES['image']
                    img_array = DeepFaceService.process_image(image_file)
                    
                    # Obtener porcentajes de emociones
                    emotion_results = DeepFaceService.analyze_emotion(img_array)
                    
                    # 4. Guardar resultados en RecognitionModel
                    RecognitionModel.objects.create(
                        RecognitionResults=emotion_results,
                        FK_User=user
                    )
                    
                except ValidationError as e:
                    return Response(
                        {'error': str(e)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except Exception as e:
                    # Log error ideally
                    return Response(
                        {'error': 'Error processing emotion analysis'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                # 5. Generar token y respuesta exitosa
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        'token': token.key,
                        'user_id': user.pk,
                        'username': user.username,
                        'emotion_analysis': emotion_results
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