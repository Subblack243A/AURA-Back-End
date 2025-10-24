from rest_framework import serializers
from ..models import UserModel

class UserLoginSerializer(serializers.Serializer):
    
    email = serializers.EmailField()
    password = serializers.CharField(
        max_length=128,
        style={'input_type': 'password'}, # Para que se vea como password en la UI de DRF
        trim_whitespace=False,
        write_only=True
    )
    
    