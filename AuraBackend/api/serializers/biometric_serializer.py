from rest_framework import serializers

class BiometricRegistrationSerializer(serializers.Serializer):
    """
    Serializer para registrar la cara de un usuario.
    Requiere un archivo de imagen y opcionalmente el ID del usuario si el administrador necesita especificarlo.
    """
    image = serializers.ImageField(required=True)
    # user_id puede ser pasado si estamos registrando para alguien más,
    # de lo contrario, asumimos request.user en la vista.
    user_id = serializers.IntegerField(required=False)

    def validate_image(self, value):
        # Validación básica si es necesario, aunque ImageField maneja las verificaciones de formato.
        return value

class BiometricRecognitionSerializer(serializers.Serializer):
    """
    Serializer para reconocer un usuario a partir de una imagen subida.
    """
    image = serializers.ImageField(required=True)
