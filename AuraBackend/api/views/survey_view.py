from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from ..serializers.survey_serializer import MbiSsSurveySerializer
from ..models import DictionaryRoleModel

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
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def post(self, request, *args, **kwargs):
        serializer = MbiSsSurveySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Guardamos la encuesta asociada al usuario autenticado
            serializer.save(FK_User=request.user)
            return Response(serializer.data['SurveyResult'], status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
