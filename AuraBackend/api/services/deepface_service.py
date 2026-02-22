import numpy as np
import cv2
import os
from datetime import datetime
from deepface import DeepFace
from rest_framework.exceptions import ValidationError
from django.conf import settings

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
            embedding_objs = DeepFace.represent(
                img_path=img_array,
                model_name="ArcFace",
                detector_backend="opencv",
                enforce_detection=True
            )
            
            if not embedding_objs:
                raise ValidationError("No se detectó ningún rostro en la imagen.")

            # Retorna el embedding del primer rostro encontrado como lista
            return list(embedding_objs[0]["embedding"])
            
        except ValueError as e:
            raise ValidationError(f"Face detection failed: {str(e)}")
        except Exception as e:
            raise ValidationError(f"Error generating embedding: {str(e)}")

    @staticmethod
    def verify_face(embedding_a, embedding_b, threshold=0.68):
        """
        Compara dos embeddings usando la distancia del coseno.
        ArcFace con distancia del coseno suele usar un umbral de ~0.68.
        Si la distancia es menor al umbral, se considera la misma persona.
        """
        try:
            # Convertir a numpy arrays para el cálculo
            a = np.array(embedding_a)
            b = np.array(embedding_b)
            
            # Calcular similitud del coseno
            # Cosine distance = 1 - ( (a . b) / (||a|| * ||b||) )
            dot_product = np.dot(a, b)
            norm_a = np.linalg.norm(a)
            norm_b = np.linalg.norm(b)
            
            cosine_similarity = dot_product / (norm_a * norm_b)
            cosine_distance = 1 - cosine_similarity
            
            print(f"DEBUG: Face verification - Cosine Distance: {cosine_distance:.4f} (Threshold: {threshold})")
            
            return cosine_distance <= threshold
        except Exception as e:
            print(f"Error verifying face: {str(e)}")
            return False

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

    @staticmethod
    def get_dominant_emotion(emotion_results):
        """
        Determina la emoción dominante de un diccionario de resultados.
        Returns: El nombre de la emoción en inglés (para usar como nombre de carpeta).
        """
        if not emotion_results:
            return 'neutral'
            
        # Mapeo invertido para volver a inglés
        reverse_map = {
            'feliz': 'happy',
            'triste': 'sad',
            'enojado': 'angry',
            'sorpresa': 'surprise',
            'miedo': 'fear',
            'disgusto': 'disgust',
            'neutral': 'neutral'
        }
        
        # Encontrar la clave con el valor máximo
        dominant_es = max(emotion_results, key=emotion_results.get)
        return reverse_map.get(dominant_es, 'neutral')

    @staticmethod
    def save_image_by_emotion(img_array, emotion_results):
        """
        Guarda la imagen en la carpeta correspondiente a su emoción dominante.
        """
        try:
            dominant_en = DeepFaceService.get_dominant_emotion(emotion_results)
            
            # Ruta base del dataset (ajustada a la estructura del proyecto)
            # El usuario especificó: /home/subblack/Documentos/DevAura/AURA-Back-End/dataset
            dataset_path = os.path.join(settings.BASE_DIR, '..', 'dataset')
            target_dir = os.path.join(dataset_path, dominant_en)
            
            # Asegurar que el directorio existe
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                
            # Generar nombre de archivo único
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"capture_{timestamp}.jpg"
            file_path = os.path.join(target_dir, filename)
            
            # Guardar imagen usando OpenCV
            cv2.imwrite(file_path, img_array)
            return file_path
        except Exception as e:
            # No bloqueamos el login si falla el guardado de la imagen
            print(f"Error saving image to dataset: {str(e)}")
            return None
