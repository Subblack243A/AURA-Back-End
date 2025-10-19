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
        user = UserModel.objects.create_user(**validated_data)
        
        user.save()
        return user