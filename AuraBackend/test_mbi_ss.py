import os
import sys
import django

# Configuración de entorno Django
sys.path.append('/home/subblack/aura/AURA-Back-End/AuraBackend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AuraBackend.settings')
django.setup()

from api.serializers.survey_serializer import MbiSsSurveySerializer

def test_calculation_logic():
    # Caso 1: Respuestas que deberían dar Burnout (EE Alto, C Alto, AE Bajo)
    # EE: 0, 3, 6, 9, 12 -> 6+6+6+6+6 = 30 (Alto)
    # C: 1, 4, 10, 13 -> 6+6+6+6 = 24 (Alto)
    # AE: 2, 5, 7, 8, 11, 14 -> 6, 6, 6, 6, 6, 6 -> Invertidos (6-6)=0 -> Suma 0 (Bajo)
    burnout_answers = [0] * 15
    # EE indices
    for i in [0, 3, 6, 9, 12]: burnout_answers[i] = 6
    # C indices
    for i in [1, 4, 10, 13]: burnout_answers[i] = 6
    # AE indices (para que sea bajo invertido, el original debe ser alto)
    for i in [2, 5, 7, 8, 11, 14]: burnout_answers[i] = 6
    
    serializer = MbiSsSurveySerializer()
    results = serializer.calculate_mbi_ss(burnout_answers)
    
    print("--- Test Burnout Positivo ---")
    print(f"Scores: {results['scores']}")
    print(f"Levels: {results['levels']}")
    print(f"Has Burnout: {results['has_burnout']}")
    assert results['has_burnout'] == True
    assert results['levels']['ee_level'] == 'Alto'
    assert results['levels']['c_level'] == 'Alto'
    assert results['levels']['ae_level'] == 'Bajo'

    # Caso 2: Respuestas que NO deberían dar Burnout (EE Bajo, C Bajo, AE Alto)
    # EE -> 0 (Bajo)
    # C -> 0 (Bajo)
    # AE -> Original 0 -> Invertido (6-0)=6 -> Suma 36 (Alto)
    no_burnout_answers = [0] * 15
    results_no = serializer.calculate_mbi_ss(no_burnout_answers)
    
    print("\n--- Test Burnout Negativo ---")
    print(f"Scores: {results_no['scores']}")
    print(f"Levels: {results_no['levels']}")
    print(f"Has Burnout: {results_no['has_burnout']}")
    assert results_no['has_burnout'] == False
    assert results_no['levels']['ee_level'] == 'Bajo'
    assert results_no['levels']['c_level'] == 'Bajo'
    assert results_no['levels']['ae_level'] == 'Alto'

    print("\n¡Pruebas lógicas completadas con éxito!")

if __name__ == "__main__":
    test_calculation_logic()
