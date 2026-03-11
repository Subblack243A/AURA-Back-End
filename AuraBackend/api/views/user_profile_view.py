from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from datetime import timedelta
from api.models.tables.user_model import UserModel
from api.serializers.user_profile_serializer import UserProfileSerializer

class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

class ProfileRequestUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        
        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()

        # Send Email
        try:
            send_mail(
                'Código de Verificación para Actualización de Perfil - Aura',
                f'Hola {user.first_name},\n\nHas solicitado actualizar tu perfil en Aura. Tu código de verificación es: {otp}\n\nEste código expirará en 10 minutos.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            return Response({'message': 'Código OTP enviado al correo.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Error al enviar el correo: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ProfileUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        otp_code = request.data.get('otp_code')

        if not otp_code:
            return Response({'error': 'El código OTP es requerido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate OTP
        if user.otp_code != otp_code:
            return Response({'error': 'Código OTP incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check expiration (10 minutes)
        if not user.otp_created_at or timezone.now() > user.otp_created_at + timedelta(minutes=10):
            return Response({'error': 'El código OTP ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid, proceed with update
        serializer = UserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # Nullify OTP after successful use
            user.otp_code = None
            user.otp_created_at = None
            user.save()
            
            return Response({
                'message': 'Perfil actualizado correctamente.',
                'user': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
