from django.contrib.auth.models import AbstractUser
from django.db import models
from pgvector.django import VectorField

# Control de autentifiación y autorización de usuarios
class UserModel(AbstractUser):
    
    ID_User = models.AutoField(primary_key=True)
    FK_Role = models.ForeignKey('DictionaryRoleModel', on_delete=models.CASCADE)
    FK_Program = models.ForeignKey('DictionaryProgramModel', on_delete=models.CASCADE)
    FK_Faculty = models.ForeignKey('DictionaryFacultyModel', on_delete=models.CASCADE)
    DateOfBirth = models.DateField()
    Face = VectorField(dimensions=512, null=True, blank=True)
    FK_HealthcareProfessional = models.ForeignKey('UserModel', on_delete=models.CASCADE, null=True)
    DataAuth = models.BooleanField(default=False)
    Semester = models.IntegerField()