from django.db import models

class SurveyModel(models.Model):
    ID_Survey = models.AutoField(primary_key=True)
    FK_User = models.ForeignKey('UserModel', on_delete=models.CASCADE)
    SurveyName = models.CharField(max_length=255)
    SurveyResult = models.JSONField(default=dict, blank=True)
    SurveyDate = models.DateTimeField(auto_now_add=True)