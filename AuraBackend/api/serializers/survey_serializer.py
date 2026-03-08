from rest_framework import serializers
from ..models import SurveyModel

class MbiSsSurveySerializer(serializers.ModelSerializer):
    # Definimos los campos que esperamos en el JSON de entrada (items 1 a 15)
    # Usaremos un DictField o campos individuales. Dado que el usuario sugirió
    # item_1 a item_15 o un campo JSON, usaremos campos individuales para validación robusta.
    
    answers = serializers.ListField(
        child=serializers.IntegerField(min_value=0, max_value=6),
        min_length=15,
        max_length=15,
        write_only=True
    )

    class Meta:
        model = SurveyModel
        fields = ['ID_Survey', 'FK_User', 'SurveyName', 'SurveyResult', 'SurveyDate', 'answers']
        read_only_fields = ['ID_Survey', 'SurveyResult', 'SurveyDate', 'FK_User', 'SurveyName']

    def validate_answers(self, value):
        if len(value) != 15:
            raise serializers.ValidationError("Se requieren exactamente 15 respuestas.")
        return value

    def calculate_mbi_ss(self, answers):
        # Mapeo de ítems (1-indexed en el requerimiento, 0-indexed en la lista)
        # EE: 1, 4, 7, 10, 13 -> indices 0, 3, 6, 9, 12
        ee_indices = [0, 3, 6, 9, 12]
        # C: 2, 5, 11, 14 -> indices 1, 4, 10, 13
        c_indices = [1, 4, 10, 13]
        # AE: 3, 6, 8, 9, 12, 15 -> indices 2, 5, 7, 8, 11, 14
        ae_indices = [2, 5, 7, 8, 11, 14]

        ee_score = sum(answers[i] for i in ee_indices)
        c_score = sum(answers[i] for i in c_indices)
        # AE requiere inversión: (6 - valor)
        ae_score = sum((6 - answers[i]) for i in ae_indices)

        # Baremos temporales basados en el plan de implementación
        levels = self.get_levels(ee_score, c_score, ae_score)
        
        # Diagnóstico Final
        # has_burnout solo si: ee 'Alto', c 'Alto', ae 'Bajo'
        has_burnout = (
            levels['ee_level'] == 'Alto' and 
            levels['c_level'] == 'Alto' and 
            levels['ae_level'] == 'Bajo'
        )

        return {
            "raw_answers": answers,
            "scores": {
                "emotional_exhaustion_score": ee_score,
                "cynicism_score": c_score,
                "academic_efficacy_score": ae_score
            },
            "levels": levels,
            "has_burnout": has_burnout
        }

    def get_levels(self, ee, c, ae):
        # EE (0-30): Bajo: 0-10, Medio: 11-20, Alto: 21-30
        if ee <= 10: ee_lvl = 'Bajo'
        elif ee <= 20: ee_lvl = 'Medio'
        else: ee_lvl = 'Alto'

        # C (0-24): Bajo: 0-8, Medio: 9-16, Alto: 17-24
        if c <= 8: c_lvl = 'Bajo'
        elif c <= 16: c_lvl = 'Medio'
        else: c_lvl = 'Alto'

        # AE (0-36): Bajo: 0-12, Medio: 13-24, Alto: 25-36
        if ae <= 12: ae_lvl = 'Bajo'
        elif ae <= 24: ae_lvl = 'Medio'
        else: ae_lvl = 'Alto'

        return {
            "ee_level": ee_lvl,
            "c_level": c_lvl,
            "ae_level": ae_lvl
        }

    def create(self, validated_data):
        answers = validated_data.pop('answers')
        results = self.calculate_mbi_ss(answers)
        
        # El resto de campos del modelo
        validated_data['SurveyName'] = 'MBI-SS'
        validated_data['SurveyResult'] = results
        
        # El usuario se obtiene del contexto (request.user) en la vista, 
        # pero aquí lo asignamos si viene en validated_data (que vendrá de la vista)
        return super().create(validated_data)
