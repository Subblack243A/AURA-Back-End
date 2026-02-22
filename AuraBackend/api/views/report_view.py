from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema, OpenApiExample
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
    """Permiso para usuarios con rol de Profesional de la Salud."""
    def has_permission(self, request, view):
        return RoleConfirmationService.is_healthcare_professional(request.user)

class IsNotAdminRole(permissions.BasePermission):
    """Permiso para cualquier usuario autenticado que NO sea administrador."""
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated) and not RoleConfirmationService.is_admin(request.user)

class AdminReportView(APIView):
    """
    Vista para generar reportes generales de emociones para el administrador.
    Genera datos para gráficos de barras:
    1. Conteo de registros manuales por emoción.
    2. Conteo de emociones dominantes en reconocimientos faciales.
    """
    permission_classes = [IsAdminUserRole]

    @extend_schema(
        summary="Cuentas generales de emociones para el administrador",
        description="Retorna el conteo de cada emoción en registros manuales y la emoción dominante en reconocimientos faciales.",
        responses={200: dict},
        examples=[
            OpenApiExample(
                'Ejemplo de Reporte General',
                value={
                    'report_name': 'Reporte General de Emociones',
                    'manual_registrations': {
                        'feliz': 10,
                        'triste': 5,
                        'enojado': 2
                    },
                    'facial_recognition_dominance': {
                        'feliz': 8,
                        'triste': 3,
                        'neutral': 12
                    }
                },
                response_only=True,
            )
        ]
    )
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

    @extend_schema(
        summary="Promedio de emociones por usuario",
        description="Calcula el promedio de cada emoción para un usuario específico basado en sus registros de reconocimiento facial.",
        responses={200: dict},
        examples=[
            OpenApiExample(
                'Ejemplo de Reporte de Usuario',
                value={
                    'user_id': 1,
                    'total_facial_records': 5,
                    'facial_emotion_averages': {
                        'feliz': 45.5,
                        'triste': 10.2,
                        'enojado': 5.1,
                        'neutral': 39.2
                    },
                    'manual_registration_percentages': {
                        'feliz': 80.0,
                        'triste': 20.0
                    }
                },
                response_only=True,
            )
        ]
    )
    def get(self, request, user_id, *args, **kwargs):
        # 1. Procesar Reconocimientos Faciales (Averages)
        recognition_records = RecognitionModel.objects.filter(FK_User_id=user_id)
        
        facial_averages = {}
        facial_count = 0
        
        if recognition_records.exists():
            totals = {
                'feliz': 0.0, 'triste': 0.0, 'enojado': 0.0, 'sorpresa': 0.0, 
                'miedo': 0.0, 'disgusto': 0.0, 'neutral': 0.0
            }
            facial_count = recognition_records.count()

            for record in recognition_records:
                results = record.RecognitionResults
                if results and isinstance(results, dict):
                    for emotion in totals.keys():
                        totals[emotion] += results.get(emotion, 0.0)

            facial_averages = {emotion: total / facial_count for emotion, total in totals.items()}

        # 2. Procesar Registros Manuales (Percentages)
        manual_records = EmotionRegisterModel.objects.filter(FK_User_id=user_id)
        manual_count = manual_records.count()
        manual_percentages = {}

        if manual_count > 0:
            register_counts = manual_records.values(
                'FK_Emotion__Emotion'
            ).annotate(count=Count('FK_Emotion'))
            
            manual_percentages = {
                item['FK_Emotion__Emotion']: (item['count'] / manual_count) * 100 
                for item in register_counts
            }

        if not recognition_records.exists() and not manual_records.exists():
            return Response(
                {"error": "No records found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'user_id': user_id,
            'total_facial_records': facial_count,
            'facial_emotion_averages': facial_averages,
            'total_manual_records': manual_count,
            'manual_registration_percentages': manual_percentages
        }, status=status.HTTP_200_OK)

class UserTimelineReportView(APIView):
    """
    Vista para generar una línea de tiempo emocional de los últimos 7 días para un usuario.
    Combina registros manuales y reconocimientos faciales (emoción dominante).
    """
    permission_classes = [IsNotAdminRole]

    @extend_schema(
        summary="Línea de tiempo emocional de los últimos 7 días",
        description="Retorna una lista cronológica de emociones capturadas por reconocimiento facial y registros manuales.",
        responses={200: dict},
        examples=[
            OpenApiExample(
                'Ejemplo de Línea de Tiempo',
                value={
                    'user_id': 1,
                    'facial_timeline': [
                        {
                            'timestamp': '2023-10-20T14:30:00Z',
                            'emotion': 'feliz'
                        }
                    ],
                    'manual_timeline': [
                        {
                            'timestamp': '2023-10-21T09:15:00Z',
                            'emotion': 'triste'
                        }
                    ]
                },
                response_only=True,
            )
        ]
    )
    def get(self, request, user_id, *args, **kwargs):
        from django.utils import timezone
        from datetime import timedelta

        # 1. Definir el rango de tiempo (últimos 7 días)
        seven_days_ago = timezone.now() - timedelta(days=7)

        # 2. Obtener registros de Reconocimiento Facial
        facial_records = RecognitionModel.objects.filter(
            FK_User_id=user_id,
            dateOfRecognition__gte=seven_days_ago
        ).order_by('dateOfRecognition')

        facial_timeline = []

        for record in facial_records:
            results = record.RecognitionResults
            if results and isinstance(results, dict):
                try:
                    dominant_emotion = max(results, key=results.get)
                    facial_timeline.append({
                        'timestamp': record.dateOfRecognition,
                        'emotion': dominant_emotion,
                    })
                except (ValueError, TypeError):
                    continue

        # 3. Obtener registros Manuales
        manual_records = EmotionRegisterModel.objects.filter(
            FK_User_id=user_id,
            EmotionDate__gte=seven_days_ago
        ).select_related('FK_Emotion').order_by('EmotionDate')

        manual_timeline = []

        for record in manual_records:
            manual_timeline.append({
                'timestamp': record.EmotionDate,
                'emotion': record.FK_Emotion.Emotion,
            })

        if not facial_timeline and not manual_timeline:
            return Response(
                {"error": "No emotional records found for this user in the last 7 days"},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'user_id': user_id,
            'facial_timeline': facial_timeline,
            'manual_timeline': manual_timeline
        }, status=status.HTTP_200_OK)
