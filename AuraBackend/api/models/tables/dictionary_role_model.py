from django.db import models

class DictionaryRoleModel(models.Model):
    ID_Role = models.AutoField(primary_key=True, unique=True)
    RoleType = models.CharField(unique=True, max_length=255)
