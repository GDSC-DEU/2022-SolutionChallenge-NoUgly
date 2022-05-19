from json import JSONDecodeError
from django.http import JsonResponse
from django.shortcuts import redirect
from rest_framework import viewsets, permissions, status
from accounts.permissions import IsUserOrReadOnly
from allauth.socialaccount.providers.kakao import views as kakao_views
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView, SocialLoginSerializer
import requests
from allauth.socialaccount.models import SocialAccount
from .models import Destination, User
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


class KakaoException(Exception):
    pass


def kakao_login(request):
    app_rest_api_key = os.environ.get('kakao_client_id')
    redirect_uri = os.environ.get('kakao_redirect_uri')
    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )


def kakao_callback(request):
    # params = urllib.parse.urlencode(request.GET)
    # redirect_uri = os.environ.get('kakao_redirect_uri')

    # rturn redirect(f'{redirect_uri}?{params}')
    try:
        app_rest_api_key = os.environ.get('kakao_client_id')
        redirect_uri = os.environ.get('kakao_redirect_uri')
        user_token = request.GET.get("code")
        # post request
        token_request = requests.get(
            f"https://kauth.kakao.com/oauth/token?grant_type=authorization_code&client_id={app_rest_api_key}&redirect_uri={redirect_uri}&code={user_token}"
        )
        token_response_json = token_request.json()
        error = token_response_json.get("error", None)
        # if there is an error from token_request
        if error is not None:
            raise JSONDecodeError(error)
        access_token = token_response_json.get("access_token")
        print('access_token :', access_token)
        # post request
        profile_request = requests.post(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        profile_json = profile_request.json()
        # parsing profile json
        kakao_account = profile_json.get("kakao_account")
        email = kakao_account.get("email", None)
        # 이메일은 필수제공 항목이 아니므로 수정 필요 (비즈니스 채널을 연결하면 검수 신청 후 필수 변환 가능)
        profile = kakao_account.get("profile")
        nickname = profile.get("nickname")
        profile_image = profile.get("thumbnail_image_url")

        print('image :', profile_image)
        try:
            user_in_db = User.objects.get(email=email)
            # kakao계정 email이 서비스에 이미 따로 가입된 email 과 충돌한다면
            print('user_in_db :', user_in_db.user_type)
            if user_in_db.user_type != 'kakao':
                raise KakaoException()
            # if social_user is None:
            #     return JsonResponse(
            #         {'err_msg': 'email exists but not social user'}, status=status.HTTP_400_BAD_REQUEST)
            # if social_user.provider != 'kakao':
            #     return JsonResponse(
            #         {'err_msg': 'no matching social type'}, status=status.HTTP_400_BAD_REQUEST)
            # 이미 kakao로 가입된 유저라면
            else:
                # 서비스에 rest-auth 로그인
                data = {'code': user_token,
                        'access_token': access_token,
                        }
                print('data :', data)

                accept = requests.post(
                    f"http://127.0.0.1:8000/accounts/login/kakao/django",
                    data=data,
                )
                accept_status = accept.status_code
                if accept_status != 200:
                    return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)
                accept_json = accept.json()
                # accept_json.pop('user', None)
                accept_jwt = accept_json.get("token")
                User.objects.filter(email=email).update(
                    name=nickname,
                    email=email,
                    user_type='kakao',
                    is_active=True,
                )
        except User.DoesNotExist:
            # 서비스에 rest-auth 로그인
            data = {'access_token': access_token, 'code': user_token,
                    }
            print('data :', data)
            accept = requests.post(
                f"http://127.0.0.1:8000/accounts/login/kakao/django",
                data=data,
                # encoding="UTF-8"
            )
            accept_status = accept.status_code
            print('User 없을때', accept_status)
            if accept_status != 200:
                return JsonResponse({'err_msg': 'failed to signin'}, status=accept_status)

            accept_json = accept.json()
            # accept_json.pop('user', None)

            accept_jwt = accept_json.get("token")
            User.objects.filter(email=email).update(
                name=nickname,
                email=email,
                user_type='kakao',
                is_active=True,
            )

        return redirect("http://127.0.0.1:8000/")
    except KakaoException:
        return redirect("http://127.0.0.1:8000/account/login")


class KakaoToDjangoLogin(SocialLoginView):
    adapter_class = kakao_views.KakaoOAuth2Adapter
    client_class = OAuth2Client
    serializer_class = SocialLoginSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)


def naver_login(request):
    app_rest_api_key = os.environ.get('naver_client_id')
    redirect_uri = "http://127.0.0.1:8000/accounts/login/naver/callback/"
    return redirect(
        f"https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id={app_rest_api_key}&state=STATE_STRING&redirect_uri={redirect_uri}"

    )
