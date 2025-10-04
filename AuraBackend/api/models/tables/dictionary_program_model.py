from django.db import models

class DictionaryProgram(models.Model):
    ID_Program = models.AutoField(primary_key=True)
    Program = models.CharField(unique=True, max_length=100)