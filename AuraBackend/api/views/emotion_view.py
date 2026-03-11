from django.utils import timezone
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.serializers.emotion_serializer import EmotionRegisterSerializer

class EmotionRegisterView(generics.CreateAPIView):
    """
    API endpoint que permite a los usuarios registrar su emoción actual.
    La emoción debe ser un entero entre 1 y 6.
    """
    serializer_class = EmotionRegisterSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({"message": "Emotion registered successfully"}, status=status.HTTP_201_CREATED)

    def get(self, request, *args, **kwargs):
        """
        Retorna la fecha de los últimos registros de emoción del usuario.
        - last_registrations: últimos 3, usado para control de ráfagas.
        - last_manual_registration: el más reciente (o null), usado para el chequeo de 24h.
        """
        from api.models.tables.emotion_register_model import EmotionRegisterModel
        last_regs = EmotionRegisterModel.objects.filter(FK_User=request.user).order_by('-EmotionDate')[:3]
        last_regs_list = list(last_regs)

        return Response({
            "last_registrations": [reg.EmotionDate for reg in last_regs_list],
            "last_manual_registration": last_regs_list[0].EmotionDate if last_regs_list else None,
            "server_time": timezone.now()
        }, status=status.HTTP_200_OK)
