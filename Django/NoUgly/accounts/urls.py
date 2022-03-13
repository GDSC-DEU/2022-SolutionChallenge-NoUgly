from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(r'destination', DestinationViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('login/kakao/', kakao_login, name='kakao_login'),
    path('login/kakao/callback/', kakao_callback, name='kakao_callback'),
    path('login/kakao/django', KakaoToDjangoLogin.as_view(),
         name='kakao_django_login'),

]
