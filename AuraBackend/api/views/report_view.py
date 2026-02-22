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

class IsHealthcareProfessionalRole(permissions.BasePermission):
    """
    Permiso personalizado que delega la lógica al RoleConfirmationService.
    """
    def has_permission(self, request, view):
        return RoleConfirmationService.is_healthcare_professional(request.user)

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

class UserSpecificReportView(APIView):
    """
    Vista para generar reportes específicos por usuario para el Profesional de la Salud.
    Calcula el promedio de porcentajes de cada emoción en los reconocimientos faciales.
    """
    permission_classes = [IsHealthcareProfessionalRole]

    def get(self, request, user_id, *args, **kwargs):
        # Obtener todos los registros de reconocimiento para el usuario especificado
        recognition_records = RecognitionModel.objects.filter(FK_User_id=user_id)
        
        if not recognition_records.exists():
            return Response(
                {"error": "No recognition records found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Inicializamos acumuladores para las 7 emociones estándar
        totals = {
            'feliz': 0.0, 'triste': 0.0, 'enojado': 0.0, 'sorpresa': 0.0, 
            'miedo': 0.0, 'disgusto': 0.0, 'neutral': 0.0
        }
        count = recognition_records.count()

        for record in recognition_records:
            results = record.RecognitionResults
            if results and isinstance(results, dict):
                for emotion in totals.keys():
                    totals[emotion] += results.get(emotion, 0.0)

        # Calculamos los promedios
        averages = {emotion: total / count for emotion, total in totals.items()}

        return Response({
            'user_id': user_id,
            'total_records': count,
            'emotion_averages': averages
        }, status=status.HTTP_200_OK)
