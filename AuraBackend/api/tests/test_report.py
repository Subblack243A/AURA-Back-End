from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from api.models.tables.recognition_model import RecognitionModel
from api.models.tables.emotion_register_model import EmotionRegisterModel
from api.models.tables.dictionary_role_model import DictionaryRoleModel
from api.models.tables.dictionary_emotion_model import DictionaryEmotionModel
from api.models.tables.dictionary_program_model import DictionaryProgramModel
from api.models.tables.dictionary_faculty_model import DictionaryFacultyModel

class AdminReportTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        
        # Crear roles
        self.admin_role = DictionaryRoleModel.objects.create(RoleType="Administrador")
        self.user_role = DictionaryRoleModel.objects.create(RoleType="Estudiante")
        self.hp_role = DictionaryRoleModel.objects.create(RoleType="Profesional de la Salud")
        
        # Otros modelos requeridos para el usuario
        self.faculty = DictionaryFacultyModel.objects.create(Faculty="TestFaculty")
        self.program = DictionaryProgramModel.objects.create(Program="TestProgram", FK_Faculty=self.faculty)
        
        # Crear usuarios
        self.admin_user = self.user_model.objects.create_user(
            username='admin_user', email='admin@example.com', password='password123',
            FK_Role=self.admin_role, FK_Program=self.program, FK_Faculty=self.faculty,
            DateOfBirth='1990-01-01', Semester=1
        )
        self.regular_user = self.user_model.objects.create_user(
            username='regular_user', email='user@example.com', password='password123',
            FK_Role=self.user_role, FK_Program=self.program, FK_Faculty=self.faculty,
            DateOfBirth='1990-01-01', Semester=1
        )
        self.hp_user = self.user_model.objects.create_user(
            username='hp_user', email='hp@example.com', password='password123',
            FK_Role=self.hp_role, FK_Program=self.program, FK_Faculty=self.faculty,
            DateOfBirth='1990-01-01', Semester=1
        )
        
        # Crear emociones
        self.emotion_feliz = DictionaryEmotionModel.objects.create(Emotion="feliz")
        self.emotion_triste = DictionaryEmotionModel.objects.create(Emotion="triste")
        
        # Crear registros manuales
        EmotionRegisterModel.objects.create(FK_User=self.regular_user, FK_Emotion=self.emotion_feliz)
        EmotionRegisterModel.objects.create(FK_User=self.regular_user, FK_Emotion=self.emotion_feliz)
        EmotionRegisterModel.objects.create(FK_User=self.regular_user, FK_Emotion=self.emotion_triste)
        
        # Crear registros de reconocimiento
        RecognitionModel.objects.create(
            FK_User=self.regular_user, 
            RecognitionResults={'feliz': 90.0, 'triste': 10.0}
        )
        RecognitionModel.objects.create(
            FK_User=self.regular_user, 
            RecognitionResults={'feliz': 10.0, 'triste': 80.0}
        )
        
        self.report_url = '/api/reports/general/'

    def test_report_access_admin(self):
        """Test que un administrador puede acceder al reporte"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar conteos manuales
        self.assertEqual(response.data['manual_registrations']['feliz'], 2)
        self.assertEqual(response.data['manual_registrations']['triste'], 1)
        
        # Verificar conteos de reconocimiento (dominantes)
        # 1 récord: feliz (90), 1 récord: triste (80)
        self.assertEqual(response.data['facial_recognition_dominance']['feliz'], 1)
        self.assertEqual(response.data['facial_recognition_dominance']['triste'], 1)

    def test_report_access_denied_regular_user(self):
        """Test que un usuario regular no puede acceder al reporte"""
        self.client.force_authenticate(user=self.regular_user)
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_access_denied_unauthenticated(self):
        """Test que un usuario no autenticado no puede acceder al reporte"""
        response = self.client.get(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_role_service_hp(self):
        """Test que el servicio de roles reconoce al profesional de la salud"""
        from api.services.role_confirmation_service import RoleConfirmationService
        self.assertTrue(RoleConfirmationService.is_healthcare_professional(self.hp_user))
        self.assertFalse(RoleConfirmationService.is_admin(self.hp_user))
        self.assertTrue(RoleConfirmationService.is_admin(self.admin_user))
        self.assertFalse(RoleConfirmationService.is_healthcare_professional(self.admin_user))
