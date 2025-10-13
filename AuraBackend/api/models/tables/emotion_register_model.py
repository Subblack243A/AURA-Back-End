from django.db import models

class EmotionRegisterModel(models.Model):
    ID_EmotionRegister = models.AutoField(primary_key=True)
    FK_User = models.ForeignKey('User', on_delete=models.CASCADE)
    FK_Emotion = models.ForeignKey('DictionaryEmotionModel', on_delete=models.CASCADE)
    EmotionDate = models.DateTimeField(auto_now_add=True)
