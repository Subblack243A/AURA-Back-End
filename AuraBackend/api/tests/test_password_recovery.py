from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from api.models.tables.dictionary_role_model import DictionaryRoleModel
from api.models.tables.dictionary_program_model import DictionaryProgramModel
from api.models.tables.dictionary_faculty_model import DictionaryFacultyModel
from unittest.mock import patch
from django.utils import timezone

class PasswordRecoveryTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        
        self.role = DictionaryRoleModel.objects.create(RoleName="TestRole")
        self.program = DictionaryProgramModel.objects.create(ProgramName="TestProgram")
        self.faculty = DictionaryFacultyModel.objects.create(FacultyName="TestFaculty")
        
        self.email = 'test@ucundinamarca.edu.co'
        self.user = self.user_model.objects.create_user(
            username='test_user',
            email=self.email,
            password='OldPassword123',
            FK_Role=self.role,
            FK_Program=self.program,
            FK_Faculty=self.faculty,
            DateOfBirth='2000-01-01',
            Semester=1
        )
        self.user.is_active = True
        self.user.save()
        
        self.request_url = '/api/password-recovery/request/'
        self.verify_url = '/api/password-recovery/verify/'
        self.reset_url = '/api/password-recovery/reset/'

    @patch('django.core.mail.send_mail')
    def test_full_recovery_flow(self, mock_send_mail):
        """Test the complete recovery flow"""
        # 1. Request OTP
        response = self.client.post(self.request_url, {'email': self.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        otp = self.user.otp_code
        self.assertIsNotNone(otp)
        
        # 2. Verify OTP
        response = self.client.post(self.verify_url, {'email': self.email, 'otp_code': otp}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Reset Password
        new_password = 'NewPassword123'
        response = self.client.post(self.reset_url, {
            'email': self.email,
            'otp_code': otp,
            'password': new_password,
            'confirm_password': new_password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 4. Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
        self.assertIsNone(self.user.otp_code)

    def test_invalid_otp(self):
        self.user.otp_code = '111111'
        self.user.otp_created_at = timezone.now()
        self.user.save()
        
        response = self.client.post(self.verify_url, {'email': self.email, 'otp_code': '222222'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_expired_otp(self):
        from datetime import timedelta
        self.user.otp_code = '111111'
        self.user.otp_created_at = timezone.now() - timedelta(minutes=15)
        self.user.save()
        
        response = self.client.post(self.verify_url, {'email': self.email, 'otp_code': '111111'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("expirado", response.data['error'])
