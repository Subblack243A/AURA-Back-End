from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils import timezone
from datetime import timedelta
from api.models.tables.user_model import UserModel
from rest_framework.authtoken.models import Token

class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')

        if not email or not otp_code:
            return Response({'error': 'Email and OTP code are required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserModel.objects.filter(email=email).first()
            
            if not user:
                return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Check if code matches
            if user.otp_code != otp_code:
                return Response({'error': 'Código incorrecto.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check expiration (10 minutes)
            if timezone.now() > user.otp_created_at + timedelta(minutes=10):
                return Response({'error': 'El código ha expirado.'}, status=status.HTTP_400_BAD_REQUEST)

            # Success
            user.is_active = True
            user.otp_code = None # Clear code
            user.otp_created_at = None
            user.save()

            # Generate token
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'message': 'Cuenta verificada con éxito.',
                'token': token.key,
                'user_id': user.pk,
                'username': user.username,
                'role': user.FK_Role.RoleType
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
