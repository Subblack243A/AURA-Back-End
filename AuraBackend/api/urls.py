from django.urls import path, include
from rest_framework import routers
from api.views.user_viewset import UserViewSet
from api.views.user_api_view import UserView
from api.views.user_login_view import UserLoginView
from api.views.biometric_view import BiometricRegistrationView, BiometricRecognitionView
from api.views.emotion_view import EmotionRegisterView

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
]
