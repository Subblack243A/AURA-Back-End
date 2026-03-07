from django.utils import timezone
from datetime import timedelta
from rest_framework import serializers
from api.models.tables.emotion_register_model import EmotionRegisterModel
from api.models.tables.dictionary_emotion_model import DictionaryEmotionModel

class EmotionRegisterSerializer(serializers.ModelSerializer):
    emotion = serializers.IntegerField(min_value=1, max_value=6, write_only=True)

    class Meta:
        model = EmotionRegisterModel
        fields = ['emotion']

    def validate(self, data):
        user = self.context['request'].user
        now = timezone.now()
        
        # Obtener los últimos 3 registros
        last_3_regs = list(EmotionRegisterModel.objects.filter(FK_User=user).order_by('-EmotionDate')[:3])
        
        if len(last_3_regs) >= 3:
            # Si el más reciente fue hace menos de 3 minutos
            diff_from_last = now - last_3_regs[0].EmotionDate
            
            # Y la ráfaga ocurrió (3 registros en menos de 60 segundos)
            # Comparamos el más reciente de los 3 con el más antiguo de los 3
            burst_duration = last_3_regs[0].EmotionDate - last_3_regs[2].EmotionDate
            
            if burst_duration < timedelta(seconds=60) and diff_from_last < timedelta(minutes=3):
                remaining = timedelta(minutes=3) - diff_from_last
                minutes = int(remaining.total_seconds() // 60)
                seconds = int(remaining.total_seconds() % 60)
                raise serializers.ValidationError(
                    f"Demasiados intentos. Por favor, espera {minutes}m {seconds}s."
                )
        return data

    def create(self, validated_data):
        emotion_id = validated_data.pop('emotion')
        user = self.context['request'].user
        
        try:
            emotion_instance = DictionaryEmotionModel.objects.get(ID_Emotion=emotion_id)
        except DictionaryEmotionModel.DoesNotExist:
            raise serializers.ValidationError({"emotion": "Invalid emotion ID."})

        emotion_register = EmotionRegisterModel.objects.create(
            FK_User=user,
            FK_Emotion=emotion_instance
        )
        return emotion_register
