from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from api.models.tables.user_model import UserModel


class CancelRegistrationView(APIView):
    """
    DELETE endpoint to remove an inactive (unverified) user.
    This allows the user to go back from OTP verification and
    re-register with corrected data.
    """
    permission_classes = [permissions.AllowAny]

    def delete(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'El correo electrónico es requerido.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Only allow deleting users that are still inactive (not yet verified)
        user = UserModel.objects.filter(email=email, is_active=False).first()

        if not user:
            return Response(
                {'error': 'No se encontró un registro pendiente de verificación para ese correo.'},
                status=status.HTTP_404_NOT_FOUND
            )

        user.delete()

        return Response(
            {'message': 'Registro cancelado. Puedes volver a registrarte con los datos correctos.'},
            status=status.HTTP_200_OK
        )
