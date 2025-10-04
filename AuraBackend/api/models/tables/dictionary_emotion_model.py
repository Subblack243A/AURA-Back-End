from django.db import models

class DictionaryEmotion(models.Model):
    ID_Emotion = models.AutoField(primary_key=True)
    Emotion = models.CharField(unique=True, max_length=100)