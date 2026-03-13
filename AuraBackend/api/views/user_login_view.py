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
                # 0. Check if account is deactivated (Role ID 5)
                if user.FK_Role_id == 5:
                    # Get admin email for contact (using first superuser or generic)
                    admin_user = UserModel.objects.filter(is_superuser=True).first()
                    admin_email = admin_user.email if admin_user else "admin@aura.com"
                    
                    return Response(
                        {
                            'error': 'Tu cuenta ha sido desactivada.',
                            'code': 'ACCOUNT_DEACTIVATED',
                            'admin_email': admin_email,
                            'message': f'Para reactivar tu cuenta, por favor contacta al administrador en: {admin_email}'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

                # 0.1 Check if account is still pending (Role ID 1)
                if user.FK_Role_id == 1:
                    return Response(
                        {
                            'error': 'Tu cuenta está en estado pendiente de aprobación.',
                            'code': 'ACCOUNT_PENDING',
                            'message': 'Su estado actual es pendiente. Se le notificará al correo cuando su cuenta sea activada.'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )

                # Check if user is an Admin to bypass biometric check
                is_admin = user.FK_Role.RoleType == 'Administrador'

                # 1. Verificar si se envió la imagen para análisis de emociones (Skip for Admin)
                if not is_admin and 'image' not in request.FILES:
                    return Response(
                        {'error': 'Image file is required for emotion analysis'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

                emotion_results = None
                if not is_admin:
                    try:
                        # 2. Procesar imagen para obtener embedding
                        image_file = request.FILES['image']
                        img_array = DeepFaceService.process_image(image_file)
                        new_embedding = DeepFaceService.get_embedding(img_array)
                        
                        # 3. Comprobar si el usuario ya tiene un rostro registrado
                        if user.Face is None:
                            # Registro inicial: Guardar el embedding
                            user.Face = new_embedding
                            user.save()
                            print(f"DEBUG: Initial face registration for user {user.username}")
                        else:
                            # Verificación obligatoria
                            is_verified = DeepFaceService.verify_face(new_embedding, user.Face)
                            if not is_verified:
                                return Response(
                                    {'error': 'Autenticación facial fallida. Rostro no reconocido.'},
                                    status=status.HTTP_401_UNAUTHORIZED
                                )
                            print(f"DEBUG: Face verified successfully for user {user.username}")

                        # 4. Una vez verificado (o registrado), ahora sí analizar emociones
                        emotion_results = DeepFaceService.analyze_emotion(img_array)
                        
                        # 6. Guardar resultados en RecognitionModel
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
                        import traceback
                        traceback.print_exc()
                        return Response(
                            {'error': f'Error processing emotion analysis: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
                
                # 7. Generar token y respuesta exitosa
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        'token': token.key,
                        'user_id': user.pk,
                        'username': user.username,
                        'role': user.FK_Role.RoleType,
                        'emotion_analysis': emotion_results
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Check if user exists but is inactive
                if user_obj and not user_obj.is_active:
                    return Response(
                        {
                            'error': 'Email no verificado. Por favor verifica tu cuenta.',
                            'code': 'EMAIL_NOT_VERIFIED'
                        },
                        status=status.HTTP_403_FORBIDDEN
                    )
                
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