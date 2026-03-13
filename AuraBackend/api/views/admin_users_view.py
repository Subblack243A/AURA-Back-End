from rest_framework import views, status, permissions, serializers
from rest_framework.response import Response
from django.db.models import Case, When, Value, Count
from django.core.mail import send_mail
from django.conf import settings
from api.models.tables.user_model import UserModel
from api.models.tables.dictionary_role_model import DictionaryRoleModel
from api.models.tables.recognition_model import RecognitionModel
from api.models.tables.emotion_register_model import EmotionRegisterModel
from api.models.tables.survey_model import SurveyModel
from api.serializers.user_profile_serializer import UserProfileSerializer

class IsAdminRole(permissions.BasePermission):
    """
    Permiso personalizado que verifica si el usuario tiene el rol 'Administrador'.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        return request.user.FK_Role.RoleType == 'Administrador'

class AdminUserSerializer(UserProfileSerializer):
    id = serializers.IntegerField(source='ID_User', read_only=True)
    
    class Meta(UserProfileSerializer.Meta):
        fields = UserProfileSerializer.Meta.fields + ['id']

class UserListAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request):
        # Ordenar: 'pendiente' primero, luego por nombre
        users = UserModel.objects.annotate(
            is_pending=Case(
                When(FK_Role__RoleType='pendiente', then=Value(0)),
                default=Value(1)
            )
        ).order_by('is_pending', 'first_name')
        
        from api.serializers.user_profile_serializer import UserProfileSerializer
        
        # We need a serializer that includes ID for approval
        data = []
        for user in users:
            data.append({
                'id': user.ID_User,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.FK_Role.RoleType,
                'program': user.FK_Program.Program if user.FK_Program else '',
                'faculty': user.FK_Faculty.Faculty if user.FK_Faculty else ''
            })
            
        return Response(data, status=status.HTTP_200_OK)

class UserApproveAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def patch(self, request, pk):
        try:
            user_to_approve = UserModel.objects.get(pk=pk)
            
            if user_to_approve.FK_Role.RoleType != 'pendiente':
                return Response({'error': 'El usuario ya ha sido procesado o no está pendiente.'}, status=status.HTTP_400_BAD_REQUEST)

            # Obtener el rol de Profesional de la Salud
            try:
                prof_role = DictionaryRoleModel.objects.get(RoleType='Profesional de la Salud')
            except DictionaryRoleModel.DoesNotExist:
                return Response({'error': 'El rol "Profesional de la Salud" no existe en el sistema.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Actualizar rol
            user_to_approve.FK_Role = prof_role
            user_to_approve.save()

            # 1. Enviar correo al usuario aprobado
            try:
                send_mail(
                    '¡Bienvenido a AURA! Tu cuenta ha sido aprobada',
                    f'Hola {user_to_approve.first_name},\n\nNos complace informarte que tu cuenta de Profesional de la Salud ha sido aprobada. Ya puedes ingresar a la plataforma con tus credenciales.\n\nSaludos,\nEquipo AURA',
                    settings.EMAIL_HOST_USER,
                    [user_to_approve.email],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error enviando correo al usuario: {e}")

            # 2. Notificar a otros administradores
            admin_emails = UserModel.objects.filter(FK_Role__RoleType='Administrador').values_list('email', flat=True)
            if admin_emails:
                try:
                    send_mail(
                        'Notificación: Nuevo Profesional de la Salud Aprobado',
                        f'Se ha aceptado a un nuevo profesional de la salud: {user_to_approve.first_name} {user_to_approve.last_name} ({user_to_approve.email}).',
                        settings.EMAIL_HOST_USER,
                        list(admin_emails),
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Error enviando correo a admins: {e}")

            return Response({'message': 'Usuario aprobado exitosamente.'}, status=status.HTTP_200_OK)

        except UserModel.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)


class AdminUserDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ID_User', read_only=True)
    role = serializers.CharField(source='FK_Role.RoleType', read_only=True)
    role_id = serializers.IntegerField(source='FK_Role.ID_Role', read_only=True)
    program = serializers.CharField(source='FK_Program.Program', read_only=True)
    faculty = serializers.CharField(source='FK_Faculty.Faculty', read_only=True)
    recognitions_count = serializers.IntegerField(read_only=True)
    emotions_count = serializers.IntegerField(read_only=True)
    surveys_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = UserModel
        fields = [
            'id', 'ID_User', 'username', 'first_name', 'last_name', 'email', 
            'role', 'role_id', 'program', 'faculty', 'Semester', 'DateOfBirth', 
            'is_active', 'recognitions_count', 'emotions_count', 'surveys_count'
        ]


class AdminUserDetailAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminRole]

    def get(self, request, pk):
        try:
            user = UserModel.objects.prefetch_related('FK_Role', 'FK_Program', 'FK_Faculty').get(pk=pk)
            
            # Attach counts to the object so the serializer can pick them up automatically
            user.recognitions_count = RecognitionModel.objects.filter(FK_User=user).count()
            user.emotions_count = EmotionRegisterModel.objects.filter(FK_User=user).count()
            user.surveys_count = SurveyModel.objects.filter(FK_User=user).count()
            
            serializer = AdminUserDetailSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserModel.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, pk):
        try:
            user = UserModel.objects.get(pk=pk)
            
            # Special handling for deactivation via Role ID 5
            if 'is_active' in request.data:
                should_deactivate = not request.data['is_active']
                if should_deactivate:
                    user.FK_Role_id = 5  # "Desactivado"
                    # We keep is_active=True so they can reach the login logic and see the deactivation note
                    user.is_active = True 
                    user.save()

                    # Send deactivation email
                    try:
                        admin_user = UserModel.objects.filter(is_superuser=True).first()
                        admin_email = admin_user.email if admin_user else "admin@aura.com"
                        
                        send_mail(
                            'Notificación de Desactivación de Cuenta - AURA',
                            f'Hola {user.first_name},\n\n'
                            f'Te informamos que tu cuenta institucional en AURA ha sido desactivada por un administrador.\n\n'
                            f'Si deseas solicitar la reactivación de tu acceso, por favor contacta al equipo administrativo en: {admin_email}\n\n'
                            'Saludos,\nSoporte AURA',
                            settings.EMAIL_HOST_USER,
                            [user.email],
                            fail_silently=True,
                        )
                    except Exception as e:
                        print(f"Error enviando correo de desactivación: {e}")
                else:
                    # Reactivation: Assign a specific role if provided
                    # It MUST be a functional role (not Desactivado or pendiente)
                    new_role_id = request.data.get('role_id')
                    try:
                        role_id_int = int(new_role_id) if new_role_id else 0
                        if role_id_int in [1, 5] or role_id_int == 0:
                            return Response(
                                {'error': 'Se debe seleccionar un rol funcional (Estudiante, Admin o Prof. Salud) para reactivar la cuenta.'}, 
                                status=status.HTTP_400_BAD_REQUEST
                            )
                        
                        role = DictionaryRoleModel.objects.get(pk=role_id_int)
                        user.FK_Role = role
                        user.save()
                    except (ValueError, DictionaryRoleModel.DoesNotExist):
                        return Response({'error': 'El rol especificado es inválido o no existe.'}, status=status.HTTP_400_BAD_REQUEST)
                
                return Response({'message': 'Estado de cuenta actualizado.'}, status=status.HTTP_200_OK)

            # Support updating Role ID directly in general update
            if 'role_id' in request.data:
                user.FK_Role_id = request.data['role_id']
                user.save()
                # If we updated the role to something other than 5, we should probably ensure it's "active"
                # though it should already be.

            # Simple manual update for other fields
            fields_to_update = [
                'first_name', 'last_name', 'email', 'Semester', 
                'DateOfBirth', 'username'
            ]
            
            updated = False
            for field in fields_to_update:
                if field in request.data:
                    setattr(user, field, request.data[field])
                    updated = True
            
            if updated:
                user.save()
                return Response({'message': 'Usuario actualizado exitosamente.'}, status=status.HTTP_200_OK)
            
            return Response({'message': 'No se enviaron campos para actualizar.'}, status=status.HTTP_400_BAD_REQUEST)
            
        except UserModel.DoesNotExist:
            return Response({'error': 'Usuario no encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
