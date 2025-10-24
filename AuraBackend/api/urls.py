from django.urls import path, include
from rest_framework import routers
from api.views.user_viewset import UserViewSet
from api.views.user_api_view import UserView
from api.views.user_login_view import UserLoginView

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', UserView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
]
