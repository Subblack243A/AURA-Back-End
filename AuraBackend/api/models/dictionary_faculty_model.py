from django.db import models

class DictionaryFaculty(models.Model):
    ID_Faculty = models.AutoField(primary_key=True)
    Faculty = models.CharField(unique=True, max_length=100)