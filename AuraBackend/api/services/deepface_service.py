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
        Analiza las emociones y retorna un diccionario con los porcentajes de cada emoción.
        Returns: diccionario JSON con emociones en español y sus porcentajes.
        """
        try:
            analysis_objs = DeepFace.analyze(
                img_path=img_array,
                actions=['emotion'],
                detector_backend="opencv",
                enforce_detection=True
            )
            
            if not analysis_objs:
                return {}
                
            # Retorna el análisis del primer rostro encontrado
            emotions = analysis_objs[0]['emotion']
            
            # Mapeo de emociones a español
            translation_map = {
                'happy': 'feliz',
                'sad': 'triste',
                'angry': 'enojado',
                'surprise': 'sorpresa',
                'fear': 'miedo',
                'disgust': 'disgusto',
                'neutral': 'neutral'
            }
            
            # Construir el resultado traducido
            result = {}
            for en_key, es_key in translation_map.items():
                if en_key in emotions:
                    result[es_key] = emotions[en_key]
                else:
                    result[es_key] = 0.0
                    
            return result
            
        except Exception:
            # En caso de error, retornar estructura vacía o default
            # Se podría loguear el error aquí
            return {
                'feliz': 0.0,
                'triste': 0.0,
                'enojado': 0.0,
                'sorpresa': 0.0,
                'miedo': 0.0,
                'disgusto': 0.0,
                'neutral': 0.0
            }
