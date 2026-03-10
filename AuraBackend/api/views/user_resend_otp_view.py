from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from api.models.tables.user_model import UserModel
import random
import string
from django.core.mail import send_mail
from django.conf import settings

class ResendOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserModel.objects.filter(email=email).first()
            
            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            if user.is_active:
                return Response({'error': 'Esta cuenta ya está verificada.'}, status=status.HTTP_400_BAD_REQUEST)

            # Generate new 6-digit OTP
            otp = ''.join(random.choices(string.digits, k=6))
            user.otp_code = otp
            user.otp_created_at = timezone.now()
            user.save()

            # Send Email
            try:
                send_mail(
                    'Nuevo Código de Verificación - Aura',
                    f'Hola {user.first_name},\n\nTu nuevo código de verificación para Aura es: {otp}\n\nEste código expirará en 10 minutos.\n\nSi no solicitaste este código, puedes ignorar este mensaje.',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
                print(f"DEBUG: Resent verification email to {user.email}")
            except Exception as e:
                print(f"Error sending email: {e}")
                return Response({'error': 'Error enviando el correo de verificación.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({'message': 'Código reenviado con éxito.'}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
