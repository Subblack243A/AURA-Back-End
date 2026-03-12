from rest_framework import serializers
from ..models import UserModel
import re

class PasswordRecoveryRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not value.endswith('@ucundinamarca.edu.co'):
            raise serializers.ValidationError("Debes usar un correo institucional (@ucundinamarca.edu.co).")
        if not UserModel.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("No existe una cuenta activa con este correo.")
        return value

class PasswordRecoveryVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)

class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Las contraseñas no coinciden.")
        
        password = data.get('password')
        # At least 8 characters, one uppercase, one number
        if not re.match(r'^(?=.*[A-Z])(?=.*\d).{8,}$', password):
            raise serializers.ValidationError(
                "La contraseña debe tener al menos 8 caracteres, una mayúscula y un número."
            )
        return data
