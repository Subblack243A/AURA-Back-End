from django.urls import path, include
from rest_framework import routers
from api.views.user_viewset import UserViewSet
from api.views.user_api_view import UserView
from api.views.user_login_view import UserLoginView
from api.views.biometric_view import BiometricRegistrationView, BiometricRecognitionView
from api.views.emotion_view import EmotionRegisterView
from api.views.survey_view import MbiSsSurveyView

from api.views.report_view import AdminReportView, UserSpecificReportView, UserTimelineReportView
from api.views.dictionary_view import DictionaryProgramListView

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # User Endpoints
    path('register/', UserView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
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
    path('reports/user/<int:user_id>/', UserSpecificReportView.as_view(), name='report-user'),
    path('reports/user/<int:user_id>/timeline/', UserTimelineReportView.as_view(), name='report-user-timeline'),
    # Dictionary Endpoints
    path('programs/', DictionaryProgramListView.as_view(), name='program-list'),
]
