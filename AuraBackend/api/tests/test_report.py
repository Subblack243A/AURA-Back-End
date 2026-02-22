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

    def test_user_report_access_hp(self):
        """Test que un profesional de la salud puede acceder al reporte de usuario"""
        # Asegurarnos de que hay registros
        self.client.force_authenticate(user=self.hp_user)
        response = self.client.get(f'/api/reports/user/{self.regular_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar promedios
        # Record 1: feliz 90, triste 10
        # Record 2: feliz 10, triste 80
        # Promedios: feliz (90+10)/2 = 50, triste (10+80)/2 = 45
        self.assertEqual(response.data['facial_emotion_averages']['feliz'], 50.0)
        self.assertEqual(response.data['facial_emotion_averages']['triste'], 45.0)
        self.assertEqual(response.data['total_facial_records'], 2)
        
        # Verificar porcentajes manuales
        # regular_user tiene 2 feliz, 1 triste (de setUp). Total = 3
        # feliz: (2/3)*100 = 66.666...
        # triste: (1/3)*100 = 33.333...
        self.assertAlmostEqual(response.data['manual_registration_percentages']['feliz'], 66.66666666666666)
        self.assertAlmostEqual(response.data['manual_registration_percentages']['triste'], 33.33333333333333)
        self.assertEqual(response.data['total_manual_records'], 3)

    def test_user_report_access_denied_admin(self):
        """Test que un administrador no puede acceder al reporte de usuario (según lógica actual)"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/reports/user/{self.regular_user.id}/')
        # El permiso IsHealthcareProfessionalRole debería denegar el acceso
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_report_not_found(self):
        """Test que devuelve 404 si no hay registros para el usuario"""
        self.client.force_authenticate(user=self.hp_user)
        # Usuario sin registros (el propio HP no tiene registros en RecognitionModel ni manuales)
        response = self.client.get(f'/api/reports/user/{self.hp_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_timeline_access_hp(self):
        """Test que un profesional de la salud puede acceder a la línea de tiempo"""
        self.client.force_authenticate(user=self.hp_user)
        response = self.client.get(f'/api/reports/user/{self.regular_user.id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        facial_timeline = response.data['facial_timeline']
        manual_timeline = response.data['manual_timeline']
        
        # Verificar conteos (2 faciales, 3 manuales de setUp)
        self.assertEqual(len(facial_timeline), 2)
        self.assertEqual(len(manual_timeline), 3)
        
        # Verificar que están ordenados cronológicamente por separado
        for i in range(len(facial_timeline) - 1):
            self.assertTrue(facial_timeline[i]['timestamp'] <= facial_timeline[i+1]['timestamp'])
        for i in range(len(manual_timeline) - 1):
            self.assertTrue(manual_timeline[i]['timestamp'] <= manual_timeline[i+1]['timestamp'])

    def test_user_timeline_access_denied_admin(self):
        """Test que un administrador no puede acceder a la línea de tiempo (restricción específica)"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'/api/reports/user/{self.regular_user.id}/timeline/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
