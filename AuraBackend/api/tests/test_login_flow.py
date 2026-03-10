from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from api.models.tables.recognition_model import RecognitionModel
from api.models.tables.dictionary_role_model import DictionaryRoleModel
from api.models.tables.dictionary_program_model import DictionaryProgramModel
from api.models.tables.dictionary_faculty_model import DictionaryFacultyModel
import json

class UserLoginFlowTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        
        # Crear modelos de diccionario necesarios para el usuario
        self.role = DictionaryRoleModel.objects.create(RoleName="TestRole")
        self.program = DictionaryProgramModel.objects.create(ProgramName="TestProgram")
        self.faculty = DictionaryFacultyModel.objects.create(FacultyName="TestFaculty")
        
        # Crear un usuario con embedding facial
        self.user_with_face = self.user_model.objects.create_user(
            username='user_face',
            email='face@example.com',
            password='password123',
            FK_Role=self.role,
            FK_Program=self.program,
            FK_Faculty=self.faculty,
            DateOfBirth='2000-01-01',
            Face=[0.1] * 512, # Mock embedding
            Semester=1
        )
        
        # Crear un usuario SIN embedding facial
        self.user_no_face = self.user_model.objects.create_user(
            username='user_no_face',
            email='noface@example.com',
            password='password123',
            FK_Role=self.role,
            FK_Program=self.program,
            FK_Faculty=self.faculty,
            DateOfBirth='2000-01-01',
            Face=None,
            Semester=1
        )
        
        self.login_url = '/api/login/' 

    def test_login_no_face_embedding(self):
        """Test login si el usuario no tiene embedding facial"""
        data = {
            'email': 'noface@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'FACE_REGISTRATION_REQUIRED')

    def test_login_inactive_user(self):
        """Test login if the user is inactive (not verified)"""
        self.user_with_face.is_active = False
        self.user_with_face.save()
        
        data = {
            'email': 'face@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'EMAIL_NOT_VERIFIED')

    def test_login_with_face_missing_image(self):
        """Test login si el usuario tiene embedding facial pero no envía imagen"""
        data = {
            'email': 'face@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, data, format='json')
        
        # Como estamos enviando json, no hay archivo, por lo que debería fallar
        # Nota: Si la vista espera form-data para la carga de archivos, el formato json podría no funcionar para archivos de todos modos,
        # pero aquí probamos la verificación lógica de la existencia de 'image'.
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Image file is required', response.data['error'])

    @patch('api.services.deepface_service.DeepFaceService.process_image')
    @patch('api.services.deepface_service.DeepFaceService.analyze_emotion')
    def test_login_success_with_emotion_analysis(self, mock_analyze, mock_process):
        """Test full login flow with face check and emotion analysis"""
        
        # Mocking DeepFace responses
        mock_process.return_value = 'mock_img_array'
        mock_analyze.return_value = {
            'feliz': 80.0,
            'neutral': 20.0,
            'triste': 0.0,
            'enojado': 0.0,
            'sorpresa': 0.0,
            'miedo': 0.0,
            'disgusto': 0.0
        }
        
        # Crear un archivo de imagen dummy
        from django.core.files.uploadedfile import SimpleUploadedFile
        image = SimpleUploadedFile("face.jpg", b"file_content", content_type="image/jpeg")
        
        data = {
            'email': 'face@example.com',
            'password': 'password123',
            'image': image
        }
        
        # Debe usar multipart/form-data para la carga de archivos
        response = self.client.post(self.login_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('emotion_analysis', response.data)
        
        # Verificar registro en la base de datos
        recognition = RecognitionModel.objects.filter(FK_User=self.user_with_face).first()
        self.assertIsNotNone(recognition)
        self.assertEqual(recognition.RecognitionResults['feliz'], 80.0)
