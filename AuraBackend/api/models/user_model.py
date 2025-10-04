from django.db import models

class User(models.Model):
    ID_User = models.AutoField(primary_key=True)
    FK_Role = models.ForeignKey('DictionaryRole', on_delete=models.CASCADE)
    UserName = models.CharField(max_length=100, unique=True)
    FK_Program = models.ForeignKey('DictionaryProgram', on_delete=models.CASCADE)
    Email = models.EmailField(unique=True)
    UserPassword = models.CharField(max_length=255)
    FK_Faculty = models.ForeignKey('DictionaryFaculty', on_delete=models.CASCADE)
    DateOfBirth = models.DateField()
    Face = models.CharField(max_length=255, null=True)
    FK_HealthcareProfessional = models.ForeignKey('User', on_delete=models.CASCADE, null=True)
    DataAuth = models.BooleanField(default=False)
    Semester = models.IntegerField()