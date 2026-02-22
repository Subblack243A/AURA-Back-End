from rest_framework import serializers
from api.models.tables.dictionary_program_model import DictionaryProgramModel
from api.models.tables.dictionary_faculty_model import DictionaryFacultyModel

class DictionaryFacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = DictionaryFacultyModel
        fields = ['ID_Faculty', 'Faculty']

class DictionaryProgramSerializer(serializers.ModelSerializer):
    faculty = DictionaryFacultySerializer(source='FK_Faculty', read_only=True)

    class Meta:
        model = DictionaryProgramModel
        fields = ['ID_Program', 'Program', 'faculty']
