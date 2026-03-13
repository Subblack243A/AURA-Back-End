import random
import string
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from ..models import UserModel
from datetime import timedelta

class PasswordRecoveryService:
    @staticmethod
    def generate_otp(user):
        otp = ''.join(random.choices(string.digits, k=6))
        user.otp_code = otp
        user.otp_created_at = timezone.now()
        user.save()
        return otp

    @staticmethod
    def send_recovery_email(user, otp):
        try:
            send_mail(
                'Recuperación de Contraseña - Aura',
                f'Hola {user.first_name},\n\nHas solicitado restablecer tu contraseña. Tu código de verificación es: {otp}\n\nEste código expirará en 10 minutos.\n\nSi no solicitaste esto, puedes ignorar este mensaje.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            print(f"DEBUG: Recovery email sent to {user.email}")
            return True
        except Exception as e:
            print(f"Error sending recovery email: {e}")
            return False

    @staticmethod
    def verify_otp(email, otp_code):
        user = UserModel.objects.filter(email=email).first()
        if not user or user.otp_code != otp_code:
            return False, "Código inválido."
        
        # Check expiration (10 minutes)
        if user.otp_created_at < timezone.now() - timedelta(minutes=10):
            return False, "El código ha expirado."
            
        return True, user

    @staticmethod
    def reset_password(user, new_password):
        user.set_password(new_password)
        user.otp_code = None # Clear OTP after use
        user.otp_created_at = None
        user.save()
        return True
