from ..models import UserModel
from rest_framework import viewsets, permissions
from ..serializers import UserRegisterSerializer

# ViewSet for managing User entities
class UserViewSet(viewsets.ModelViewSet):
    
    queryset = UserModel.objects.all().order_by('ID_User')
    serializer_class = UserRegisterSerializer