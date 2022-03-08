from django.shortcuts import redirect
from rest_framework import viewsets, permissions
from accounts.permissions import IsUserOrReadOnly


from .models import Destination
from .serializers import DestinationSerializer
# Create your views here.
import os
import urllib


class DestinationViewSet(viewsets.ModelViewSet):
    queryset = Destination.objects.all()

    serializer_class = DestinationSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsUserOrReadOnly
    ]

    def get_queryset(self):
        user = self.request.user
        queryset = Destination.objects.filter(uIDX=user)

        return queryset


def kakao_login(request):
    app_rest_api_key = os.environ.get('kakao_client_id')
    redirect_uri = "http://127.0.0.1:8000/accounts/login/kakao/callback/"
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )


def kakao_callback(request):
    params = urllib.parse.urlencode(request.GET)
    return redirect(f'http://127.0.0.1:8000/accounts/login/kakao/callback?{params}')
