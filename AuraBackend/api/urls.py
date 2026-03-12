from django.urls import path, include
from rest_framework import routers
from api.views.user_viewset import UserViewSet
from api.views.user_api_view import UserView
from api.views.user_login_view import UserLoginView
from api.views.biometric_view import BiometricRegistrationView, BiometricRecognitionView
from api.views.emotion_view import EmotionRegisterView
from api.views.survey_view import MbiSsSurveyView
from api.views.user_profile_view import ProfileView, ProfileRequestUpdateView, ProfileUpdateView

from api.views.report_view import AdminReportView, UserSpecificReportView, UserTimelineReportView, GeneralSummaryAPIView
from api.views.dictionary_view import DictionaryProgramListView
from api.views.user_verify_view import VerifyOTPView
from api.views.user_resend_otp_view import ResendOTPView
from api.views.user_cancel_registration_view import CancelRegistrationView
from api.views.password_recovery_view import (
    PasswordRecoveryRequestView,
    PasswordRecoveryVerifyView,
    PasswordResetView
)

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # User Endpoints
    path('register/', UserView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend-otp'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('cancel-registration/', CancelRegistrationView.as_view(), name='cancel-registration'),

    # Password Recovery Endpoints
    path('password-recovery/request/', PasswordRecoveryRequestView.as_view(), name='password-recovery-request'),
    path('password-recovery/verify/', PasswordRecoveryVerifyView.as_view(), name='password-recovery-verify'),
    path('password-recovery/reset/', PasswordResetView.as_view(), name='password-recovery-reset'),

    # Profile Endpoints
    path('profile/', ProfileView.as_view(), name='profile-get'),
    path('profile/request-update/', ProfileRequestUpdateView.as_view(), name='profile-request-update'),
    path('profile/update/', ProfileUpdateView.as_view(), name='profile-update'),
    # Biometric Endpoints
    path('biometric/register/', BiometricRegistrationView.as_view(), name='biometric-register'),
    path('biometric/recognize/', BiometricRecognitionView.as_view(), name='biometric-recognize'),
    # Emotion Endpoints
    path('emotion/register/', EmotionRegisterView.as_view(), name='emotion-register'),
    # Survey Endpoints
    # Survey Endpoints (MBI-SS)
    path('surveys/mbi-ss/', MbiSsSurveyView.as_view(), name='mbi-ss-survey'),
    path('surveys/mbi-ss/last-response/', MbiSsSurveyView.as_view(), name='mbi-ss-last-response'),
    path('surveys/mbi-ss/history/', MbiSsSurveyView.as_view(), name='mbi-ss-history'),
    path('surveys/mbi-ss/submit/', MbiSsSurveyView.as_view(), name='mbi-ss-submit'),

    # Report Endpoints
    path('reports/general/', AdminReportView.as_view(), name='report-general'),
    path('reports/summary/', GeneralSummaryAPIView.as_view(), name='report-summary'),
    path('reports/user/<int:user_id>/', UserSpecificReportView.as_view(), name='report-user'),
    path('reports/user/<int:user_id>/timeline/', UserTimelineReportView.as_view(), name='report-user-timeline'),
    # Dictionary Endpoints
    path('programs/', DictionaryProgramListView.as_view(), name='program-list'),
]
