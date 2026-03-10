from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from api.models.tables.dictionary_role_model import DictionaryRoleModel
from api.models.tables.dictionary_program_model import DictionaryProgramModel
from api.models.tables.dictionary_faculty_model import DictionaryFacultyModel
from unittest.mock import patch

class ResendOTPTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()
        
        self.role = DictionaryRoleModel.objects.create(RoleName="TestRole")
        self.program = DictionaryProgramModel.objects.create(ProgramName="TestProgram")
        self.faculty = DictionaryFacultyModel.objects.create(FacultyName="TestFaculty")
        
        self.user = self.user_model.objects.create_user(
            username='test_user',
            email='test@example.com',
            password='password123',
            FK_Role=self.role,
            FK_Program=self.program,
            FK_Faculty=self.faculty,
            DateOfBirth='2000-01-01',
            Semester=1
        )
        self.user.is_active = False # Not verified
        self.user.save()
        
        self.resend_url = '/api/resend-otp/'

    @patch('django.core.mail.send_mail')
    def test_resend_otp_success(self, mock_send_mail):
        """Test success OTP resend"""
        data = {'email': 'test@example.com'}
        response = self.client.post(self.resend_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Código reenviado con éxito.')
        
        # Verify user update
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.otp_code)
        self.assertIsNotNone(self.user.otp_created_at)
        
        # Verify email call
        self.assertTrue(mock_send_mail.called)

    def test_resend_otp_user_not_found(self):
        """Test resend for non-existent user"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.resend_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_resend_otp_already_verified(self):
        """Test resend for already active user"""
        self.user.is_active = True
        self.user.save()
        
        data = {'email': 'test@example.com'}
        response = self.client.post(self.resend_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Esta cuenta ya está verificada.')
