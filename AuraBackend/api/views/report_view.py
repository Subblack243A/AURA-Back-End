from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Count
from ..models.tables.emotion_register_model import EmotionRegisterModel
from ..models.tables.recognition_model import RecognitionModel
from ..services.role_confirmation_service import RoleConfirmationService

class IsAdminUserRole(permissions.BasePermission):
    """
    Permiso personalizado que delega la lógica al RoleConfirmationService.
    """
    def has_permission(self, request, view):
        return RoleConfirmationService.is_admin(request.user)

class AdminReportView(APIView):
    """
    Vista para generar reportes generales de emociones para el administrador.
    Genera datos para gráficos de barras:
    1. Conteo de registros manuales por emoción.
    2. Conteo de emociones dominantes en reconocimientos faciales.
    """
    permission_classes = [IsAdminUserRole]

    def get(self, request, *args, **kwargs):
        # 1. Conteos de EmotionRegisterModel (Registros Manuales)
        # Agrupamos por el nombre de la emoción en el diccionario
        register_counts = EmotionRegisterModel.objects.values('FK_Emotion__Emotion').annotate(
            count=Count('FK_Emotion')
        ).order_by('FK_Emotion__Emotion')

        manual_data = {item['FK_Emotion__Emotion']: item['count'] for item in register_counts}

        # 2. Conteos de RecognitionModel (Reconocimientos Faciales)
        # Procesamos la información del JSONField para extraer la emoción dominante (valor máximo)
        recognition_records = RecognitionModel.objects.all()
        
        # Inicializamos el diccionario de resultados con las 7 emociones estándar
        facial_data = {
            'feliz': 0, 'triste': 0, 'enojado': 0, 'sorpresa': 0, 
            'miedo': 0, 'disgusto': 0, 'neutral': 0
        }

        for record in recognition_records:
            results = record.RecognitionResults
            if results and isinstance(results, dict):
                try:
                    # Obtenemos la llave (emoción) que tenga el valor numérico más alto
                    dominant_emotion = max(results, key=results.get)
                    if dominant_emotion in facial_data:
                        facial_data[dominant_emotion] += 1
                    else:
                        # Si por alguna razón hay una emoción no contemplada inicialmente
                        facial_data[dominant_emotion] = facial_data.get(dominant_emotion, 0) + 1
                except (ValueError, TypeError):
                    # En caso de que el diccionario esté vacío o los valores no sean comparables
                    continue

        return Response({
            'report_name': 'Reporte General de Emociones',
            'manual_registrations': manual_data,
            'facial_recognition_dominance': facial_data
        }, status=status.HTTP_200_OK)
