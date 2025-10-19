from django.urls import path, include
from rest_framework import routers
from api.views.user_viewset import UserViewSet

router = routers.DefaultRouter()

router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]
