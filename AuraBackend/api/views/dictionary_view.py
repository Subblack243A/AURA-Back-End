from rest_framework import generics, permissions
from api.models.tables.dictionary_program_model import DictionaryProgramModel
from api.serializers.dictionary_serializer import DictionaryProgramSerializer

class DictionaryProgramListView(generics.ListAPIView):
    """
    Returns a list of all active programs and their associated faculties.
    This endpoint is open to all users so they can register.
    """
    queryset = DictionaryProgramModel.objects.all().order_by('Program')
    serializer_class = DictionaryProgramSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
