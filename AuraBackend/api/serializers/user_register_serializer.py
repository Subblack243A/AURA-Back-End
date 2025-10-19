from rest_framework import serializers
from ..models import UserModel

# Transformacion de ojeto modelo a formato JSON y viceversa para registro de usuarios
class UserRegisterSerializer(serializers.ModelSerializer):
    # Comprobacion de llaves foraneas
    FK_Role =  serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Role.get_queryset())
    FK_Program = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Program.get_queryset())
    FK_Faculty = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Faculty.get_queryset())
    FK_HealthcareProfessional = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_HealthcareProfessional.get_queryset(), allow_null=True, required=False)
    
    class Meta:
        
        model = UserModel
        
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'DateOfBirth', 'DataAuth', 'Semester',
            'FK_Role', 'FK_Program', 'FK_Faculty', 'FK_HealthcareProfessional'
        ]
        
        extra_kwargs = { 'password': {'write_only': True} }
        
    def create(self, validated_data):
        role_data = validated_data.pop('FK_Role')
        program_data = validated_data.pop('FK_Program')
        faculty_data = validated_data.pop('FK_Faculty')
        
        date_of_birth_data = validated_data.get('DateOfBirth')
        data_auth_data = validated_data.get('DataAuth')
        semester_data = validated_data.get('Semester')
        healthcare_professional_data = validated_data.get('FK_HealthcareProfessional', None)
        
        user = UserModel.objects.create_user(**validated_data)
        
        user.FK_Role = role_data
        user.FK_Program = program_data
        user.FK_Faculty = faculty_data
        user.DateOfBirth = date_of_birth_data
        user.DataAuth = data_auth_data
        user.Semester = semester_data
        user.FK_HealthcareProfessional = healthcare_professional_data

        user.save()
        return user