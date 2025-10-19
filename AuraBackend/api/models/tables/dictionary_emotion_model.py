from django.db import models

class DictionaryEmotionModel(models.Model):
    ID_Emotion = models.AutoField(primary_key=True)
    Emotion = models.CharField(unique=True, max_length=100)
    
    def __str__(self):
        return self.Emotion