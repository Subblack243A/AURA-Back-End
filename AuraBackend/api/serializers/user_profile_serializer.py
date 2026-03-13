from rest_framework import serializers
from api.models.tables.user_model import UserModel
from api.models.tables.dictionary_role_model import DictionaryRoleModel
from api.models.tables.dictionary_program_model import DictionaryProgramModel
from api.models.tables.dictionary_faculty_model import DictionaryFacultyModel

class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='FK_Role.RoleType', read_only=True)
    program_name = serializers.CharField(source='FK_Program.Program', read_only=True)
    faculty_name = serializers.CharField(source='FK_Faculty.Faculty', read_only=True)
    
    # Rename model fields to match requested generic names
    birth_date = serializers.DateField(source='DateOfBirth')
    program = serializers.PrimaryKeyRelatedField(source='FK_Program', queryset=DictionaryProgramModel.objects.all())
    faculty = serializers.PrimaryKeyRelatedField(source='FK_Faculty', queryset=DictionaryFacultyModel.objects.all())
    semester = serializers.IntegerField(source='Semester')
    
    class Meta:
        model = UserModel
        fields = [
            'email', 'first_name', 'last_name', 'role', 
            'program', 'program_name', 'faculty', 'faculty_name', 
            'semester', 'birth_date'
        ]
        read_only_fields = ['email', 'role']

    def update(self, instance, validated_data):
        # Ensure email and role are not updated even if passed
        validated_data.pop('email', None)
        validated_data.pop('FK_Role', None)
        return super().update(instance, validated_data)
