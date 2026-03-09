from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..models.tables.survey_model import SurveyModel
from ..serializers.survey_serializer import MbiSsSurveySerializer
from rest_framework.authentication import TokenAuthentication

class IsStudent(permissions.BasePermission):
    """
    Permiso personalizado para asegurar que solo usuarios con rol de estudiante (ID 2)
    puedan acceder al endpoint.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # El rol de estudiante tiene ID_Role = 2 según UserRegisterSerializer
        return request.user.FK_Role_id == 2

class MbiSsSurveyView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get(self, request, *args, **kwargs):
        # Si se solicita la fecha de la última respuesta
        if 'last-response' in request.path:
            last_survey = SurveyModel.objects.filter(FK_User=request.user, SurveyName='MBI-SS').order_by('-SurveyDate').first()
            return Response({
                'last_response_date': last_survey.SurveyDate.strftime('%Y-%m-%d') if last_survey else None
            })
        
        # De lo contrario, devolver historial
        surveys = SurveyModel.objects.filter(FK_User=request.user, SurveyName='MBI-SS').order_by('-SurveyDate')
        return Response([
            {
                'id': s.ID_Survey,
                'created_at': s.SurveyDate,
                'has_burnout': s.SurveyResult.get('has_burnout', False)
            } for s in surveys
        ])

    def post(self, request, *args, **kwargs):
        serializer = MbiSsSurveySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Guardamos la encuesta asociada al usuario autenticado
            serializer.save(FK_User=request.user)
            return Response(serializer.data['SurveyResult'], status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
