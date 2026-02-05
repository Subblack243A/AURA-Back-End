import numpy as np
import cv2
from deepface import DeepFace
from rest_framework.exceptions import ValidationError

class DeepFaceService:
    @staticmethod
    def process_image(image_file):
        """
        Convierte la imagen subida (InMemoryUploadedFile) a un numpy array (BGR).
        """
        try:
            # Leer imagen en memoria
            file_bytes = np.frombuffer(image_file.read(), np.uint8)
            # Decodificar imagen usando OpenCV
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            
            if img is None:
                raise ValueError("No se pudo decodificar la imagen")
                
            return img
        except Exception as e:
            raise ValidationError(f"Formato de imagen inválido: {str(e)}")

    @staticmethod
    def get_embedding(img_array):
        """
        Genera un embedding de 512 dimensiones usando ArcFace.
        Returns: el embedding como una lista de floats.
        """
        try:
            # represent() devuelve una lista de diccionarios. Tomamos el primer rostro encontrado.
            # Usando enforce_detection=True (default) aseguramos que si no se detecta un rostro, se lance una excepción.
            embedding_objs = DeepFace.represent(
                img_path=img_array,
                model_name="ArcFace",
                detector_backend="opencv",
                enforce_detection=True
            )
            
            if not embedding_objs:
                raise ValidationError("No se detectó ningún rostro en la imagen.")

            # Retorna el embedding del primer rostro encontrado
            return embedding_objs[0]["embedding"]
            
        except ValueError as e:
            # DeepFace lanza ValueError si no se detecta un rostro cuando enforce_detection=True
            raise ValidationError(f"Face detection failed: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error generating embedding: {str(e)}")

    @staticmethod
    def analyze_emotion(img_array):
        """
        Analiza las emociones y retorna la emoción predominante.
        Returns: la emoción predominante como una cadena de texto.
        """
        try:
            analysis_objs = DeepFace.analyze(
                img_path=img_array,
                actions=['emotion'],
                detector_backend="opencv",
                enforce_detection=True
            )
            
            if not analysis_objs:
                return "neutral" # Valor por defecto
                
            # Retorna la emoción predominante del primer rostro encontrado
            return analysis_objs[0]['dominant_emotion']
            
        except Exception:
            # Si el análisis de emociones falla, retorna "unknown" de manera grácil en lugar de bloquear el flujo de autenticación
            return "unknown"
