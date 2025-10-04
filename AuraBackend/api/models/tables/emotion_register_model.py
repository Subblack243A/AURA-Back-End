from django.db import models

class EmotionRegister(models.Model):
    ID_EmotionRegister = models.AutoField(primary_key=True)
    FK_User = models.ForeignKey('User', on_delete=models.CASCADE)
    FK_Emotion = models.ForeignKey('DictionaryEmotion', on_delete=models.CASCADE)
    EmotionDate = models.DateTimeField(auto_now_add=True)
