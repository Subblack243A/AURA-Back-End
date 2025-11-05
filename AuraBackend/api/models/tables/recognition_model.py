from django.db import models

class RecognitionModel(models.Model):
    ID_Recognition = models.AutoField(primary_key=True, unique=True)
    RecognitionResults = models.JSONField(default=dict, blank=True)
    FK_User = models.ForeignKey('UserModel', on_delete=models.CASCADE)
    dateOfRecognition = models.DateTimeField(auto_now_add=True)
