from django.db import models

class Survey(models.Model):
    ID_Survey = models.AutoField(primary_key=True)
    FK_User = models.ForeignKey('User', on_delete=models.CASCADE)
    FK_SurveyResult = models.ForeignKey('SurveyResult', on_delete=models.CASCADE)
    SurveyuDate = models.DateTimeField(auto_now_add=True)