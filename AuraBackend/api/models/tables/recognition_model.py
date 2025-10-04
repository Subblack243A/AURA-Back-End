from django.db import models

class Recognition(models.Model):
    ID_Recognition = models.AutoField(primary_key=True, unique=True)
    RecognitionResults = models.CharField(max_length=255)
    FK_User = models.ForeignKey('User', on_delete=models.CASCADE)
    dateOfRecognition = models.DateTimeField(auto_now_add=True)
