from rest_framework import serializers
from ..models import UserModel

# Transformacion de ojeto modelo a formato JSON y viceversa para registro de usuarios
class UserRegisterSerializer(serializers.ModelSerializer):
    # Comprobacion de llaves foraneas
    FK_Role =  serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Role.get_queryset())
    FK_Program = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Program.get_queryset())
    FK_Faculty = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_Faculty.get_queryset())
    FK_HealthcareProfessional = serializers.PrimaryKeyRelatedField(queryset=UserModel.FK_HealthcareProfessional.get_queryset(), allow_null=True, required=False)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        
        model = UserModel
        
        fields = [
            'username', 'email', 'password', 'first_name', 'last_name', 'DateOfBirth', 'DataAuth', 'Semester',
            'FK_Role', 'FK_Program', 'FK_Faculty', 'FK_HealthcareProfessional', 'confirm_password'
        ]
        extra_kwargs = { 'password': {'write_only': True} }
        
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data
        
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        
        # Logica de roles
        role = validated_data.get('FK_Role')
        if role:
            # ID 3: Health Professional
            if role.ID_Role == 3:
                # Reassign to ID 1: Inactive
                from api.models.tables.dictionary_role_model import DictionaryRoleModel
                try:
                    inactive_role = DictionaryRoleModel.objects.get(ID_Role=1)
                    validated_data['FK_Role'] = inactive_role
                except DictionaryRoleModel.DoesNotExist:
                    raise serializers.ValidationError({"FK_Role": "Inactive role (ID 1) configuration missing."})
            
            # ID 2: Estudiante
            elif role.ID_Role == 2:
                pass # Allow registration
            
            # Cualquier otro rol (ej. Admin) está prohibido mediante registro público
            else:
                 raise serializers.ValidationError({"FK_Role": "Invalid role selected for registration."})

        user = UserModel.objects.create_user(**validated_data)
        
        user.save()
        return user