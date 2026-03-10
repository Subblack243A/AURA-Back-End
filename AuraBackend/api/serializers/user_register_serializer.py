from rest_framework import serializers
from ..models import UserModel
import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings

# Transformacion de ojeto modelo a formato JSON y viceversa para registro de usuarios
class UserRegisterSerializer(serializers.ModelSerializer):
    # Comprobacion de llaves foraneas
    FK_Role =  serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Role.get_queryset())
    FK_Program = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Program.get_queryset())
    FK_Faculty = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Faculty.get_queryset())
    FK_HealthcareProfessional = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_HealthcareProfessional.get_queryset(), allow_null=True, required=False)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        
        model = UserModel
        
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'DateOfBirth', 'DataAuth', 'Semester',
            'FK_Role', 'FK_Program', 'FK_Faculty', 'FK_HealthcareProfessional', 'confirm_password'
        ]
        extra_kwargs = { 'password': {'write_only': True} }
        
    def validate(self, data):
        # Validar coincidencia de contraseñas
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        
        # Validar dominio de correo institucional
        email = data.get('email', '')
        if not email.endswith('@ucundinamarca.edu.co'):
            raise serializers.ValidationError({"email": "Debes registrarte con un correo institucional (@ucundinamarca.edu.co)."})
            
        return data
        
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        email = validated_data.get('email')
        
        # Check if user already exists but is inactive
        user = UserModel.objects.filter(email=email, is_active=False).first()
        
        if user:
            # Update existing inactive user
            for attr, value in validated_data.items():
                if attr == 'password':
                    user.set_password(value)
                else:
                    setattr(user, attr, value)
            print(f"DEBUG: Updating existing inactive user: {email}")
        else:
            # Create new user
            user = UserModel.objects.create_user(**validated_data)
            user.is_active = False # Deactivate until OTP verified
            print(f"DEBUG: Created new inactive user: {email}")
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send Email
        try:
            send_mail(
                'Código de Verificación - Aura',
                f'Hola {user.first_name},\n\nTu código de verificación para Aura es: {otp}\n\nEste código expirará en 10 minutos.\n\nSi no solicitaste este código, puedes ignorar este mensaje.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            print(f"DEBUG: Verification email sent to {user.email}")
        except Exception as e:
            # We log the error but don't fail registration here for now (in dev)
            print(f"Error sending email: {e}")

        return user