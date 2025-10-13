from django.db import models

class SurveyModel(models.Model):
    ID_Survey = models.AutoField(primary_key=True)
    FK_User = models.ForeignKey('UserModel', on_delete=models.CASCADE)
    FK_SurveyResult = models.ForeignKey('SurveyResultModel', on_delete=models.CASCADE)
    SurveyuDate = models.DateTimeField(auto_now_add=True)