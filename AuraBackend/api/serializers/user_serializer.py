# Transformation of Python data to JSON for communication
from rest_framework import serializers
from models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['ID_User', 'UserName', 'Email', 'UserPassword', 'Face', 'DataAuth', 'Semester', 'DateOfBirth', 'FK_Role', 'FK_Program', 'FK_Faculty', 
                'FK_HealthcareProfessional']
        read_only_fields = ['ID_User', 'Email', 'UserPassword', 'DataAuth', 'FK_Program', 'FK_Faculty']