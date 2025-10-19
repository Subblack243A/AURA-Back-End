from django.db import models

class DictionaryProgramModel(models.Model):
    ID_Program = models.AutoField(primary_key=True)
    Program = models.CharField(unique=True, max_length=100)
    FK_Faculty = models.ForeignKey('DictionaryFacultyModel', on_delete=models.CASCADE, related_name='programs')
    
    def __str__(self):
        return self.Program