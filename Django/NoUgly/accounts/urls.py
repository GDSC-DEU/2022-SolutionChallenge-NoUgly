from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'destination', DestinationViewSet)


urlpatterns = [
    path('login/kakao/', kakao_login, name='kakao_login'),
    path('login/kakao/callback', kakao_callback, name='kakao_callback'),
    path('', include(router.urls)),

]
