from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions
from django.shortcuts import get_object_or_404
from pgvector.django import CosineDistance

from api.models.tables.user_model import UserModel
from api.serializers.biometric_serializer import BiometricRegistrationSerializer, BiometricRecognitionSerializer
from api.services.deepface_service import DeepFaceService

class BiometricRegistrationView(APIView):
    """
    Endpoint para registrar un embedding facial para un usuario.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BiometricRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                image_file = serializer.validated_data['image']
                
                # Determinar a qué usuario se le va a registrar el embedding:
                # Si user_id se proporciona y el solicitante es superusuario, actualizar ese usuario.
                # De lo contrario, actualizar al usuario solicitante.
                target_user = request.user
                if 'user_id' in serializer.validated_data and request.user.is_superuser:
                    target_user = get_object_or_404(UserModel, pk=serializer.validated_data['user_id'])
                
                # Procesar la imagen
                img_array = DeepFaceService.process_image(image_file)
                
                # Generar el embedding
                embedding = DeepFaceService.get_embedding(img_array)
                
                # Guardar el embedding en el perfil del usuario
                target_user.Face = embedding
                target_user.save()
                
                return Response(
                    {"message": "Face registration successful.", "user_id": target_user.pk},
                    status=status.HTTP_200_OK
                )
                
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BiometricRecognitionView(APIView):
    """
    Endpoint para reconocer un usuario a partir de una imagen facial y analizar emociones.
    """
    permission_classes = [permissions.AllowAny] # Puede ser abierto o restringido dependiendo del caso de uso

    def post(self, request, *args, **kwargs):
        serializer = BiometricRecognitionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                image_file = serializer.validated_data['image']
                
                # Procesar la imagen
                img_array = DeepFaceService.process_image(image_file)
                
                # Generar el embedding
                # Nota: Esto puede lanzar una excepción si no se detecta un rostro
                embedding = DeepFaceService.get_embedding(img_array)
                
                # Analizar la emoción (puede ser paralelizado pero manteniendo simple por ahora)
                dominant_emotion = DeepFaceService.analyze_emotion(img_array)
                
                # Búsqueda de vector usando distancia coseno
                # Interpretamos la distancia coseno como (1 - similitud coseno).
                # Lower distance means higher similarity.
                # Threshold: 0.4 is a common starting point for DeepFace/ArcFace verification.
                threshold = 0.4
                
                # Buscar el usuario más cercano
                # Anotamos con 'distance' basado en CosineDistance al embedding de entrada
                closest_match = UserModel.objects.annotate(
                    distance=CosineDistance('Face', embedding)
                ).order_by('distance').first()
                
                if closest_match and closest_match.distance is not None and closest_match.distance < threshold:
                    return Response({
                        "identified": True,
                        "user_id": closest_match.pk,
                        "username": closest_match.username,
                        "confidence_score": 1 - closest_match.distance, # Aproximación bruta
                        "dominant_emotion": dominant_emotion
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        "identified": False,
                        "message": "User not recognized.",
                        "dominant_emotion": dominant_emotion
                    }, status=status.HTTP_200_OK) # Retornar 200 con resultado es común para bio-auth
                    
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
