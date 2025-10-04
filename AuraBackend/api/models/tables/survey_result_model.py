from django.db import models

class SurveyResult(models.Model):
    ID_SurveyResult = models.AutoField(primary_key=True)
    Result = models.CharField(unique=True, max_length=100)