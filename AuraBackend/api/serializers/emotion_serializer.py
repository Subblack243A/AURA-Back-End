from rest_framework import serializers
from api.models.tables.emotion_register_model import EmotionRegisterModel
from api.models.tables.dictionary_emotion_model import DictionaryEmotionModel

class EmotionRegisterSerializer(serializers.ModelSerializer):
    emotion = serializers.IntegerField(min_value=1, max_value=6, write_only=True)

    class Meta:
        model = EmotionRegisterModel
        fields = ['emotion']

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
