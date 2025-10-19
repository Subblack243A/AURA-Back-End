from django.db import models

class DictionaryFacultyModel(models.Model):
    ID_Faculty = models.AutoField(primary_key=True)
    Faculty = models.CharField(unique=True, max_length=100)
    
    def __str__(self):
        return self.Faculty