from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..serializers.password_recovery_serializer import (
    PasswordRecoveryRequestSerializer,
    PasswordRecoveryVerifySerializer,
    PasswordResetSerializer
)
from ..services.password_recovery_service import PasswordRecoveryService
from ..models import UserModel

class PasswordRecoveryRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordRecoveryRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = UserModel.objects.filter(email=email).first()
            otp = PasswordRecoveryService.generate_otp(user)
            sent = PasswordRecoveryService.send_recovery_email(user, otp)
            if sent:
                return Response({"message": "Código de recuperación enviado."}, status=status.HTTP_200_OK)
            return Response({"error": "Error al enviar el correo."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordRecoveryVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordRecoveryVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            success, result = PasswordRecoveryService.verify_otp(email, otp_code)
            if success:
                return Response({"message": "Código verificado correctamente."}, status=status.HTTP_200_OK)
            return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']
            password = serializer.validated_data['password']
            
            success, result = PasswordRecoveryService.verify_otp(email, otp_code)
            if success:
                user = result
                PasswordRecoveryService.reset_password(user, password)
                return Response({"message": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)
            return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
