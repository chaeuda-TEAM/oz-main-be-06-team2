import requests
from a_apis.auth.cookies import create_auth_response
from ninja.errors import HttpError
from rest_framework_simplejwt.tokens import RefreshToken

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

User = get_user_model()


class GoogleAuthService:
    @staticmethod
    def create_or_get_user(email: str, name: str) -> User:
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": email, "is_email_verified": True}
        )

        if created:
            user.first_name = name.split()[0] if name else ""
            user.last_name = " ".join(name.split()[1:]) if len(name.split()) > 1 else ""
            user.save()

        return user

    @staticmethod
    def start_google_auth(server_base_url: str, client_id: str) -> str:
        redirect_uri = f"{server_base_url}/auth/google/callback"
        scope = "https://www.googleapis.com/auth/userinfo.email"
        response_type = "code"

        return (
            "https://accounts.google.com/o/oauth2/auth"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&scope={scope}"
            f"&response_type={response_type}"
            "&access_type=offline"
        )

    @staticmethod
    def callback_google_auth(
        code: str,
        server_base_url: str,
        client_id: str,
        client_secret: str,
        login_redirect_url: str,
    ):
        if not code:
            raise HttpError(400, "No code provided by Google")

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": f"{server_base_url}/auth/google/callback",
            "grant_type": "authorization_code",
        }

        token_resp = requests.post(token_url, data=data)
        if token_resp.status_code != 200:
            raise HttpError(400, "Failed to exchange code for token")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HttpError(400, "No access_token received")

        userinfo_url = f"https://www.googleapis.com/oauth2/v1/userinfo?alt=json&access_token={access_token}"
        userinfo_resp = requests.get(userinfo_url)
        if userinfo_resp.status_code != 200:
            raise HttpError(400, "Failed to get user info from Google")

        user_info = userinfo_resp.json()
        email = user_info.get("email")
        name = user_info.get("name", "")
        if not email:
            raise HttpError(400, "No email in user info")

        user = GoogleAuthService.create_or_get_user(email=email, name=name)
        refresh = RefreshToken.for_user(user)

        return {
            "success": True,
            "message": "Google 로그인 성공",
            "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
            "user": {"email": user.email},
            "redirect_url": login_redirect_url,
        }


class KakaoAuthService:
    @staticmethod
    def create_or_get_user(email: str, nickname: str) -> User:
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": nickname, "is_email_verified": True}
        )

        if created:
            user.first_name = nickname
            user.save()

        return user

    @staticmethod
    def start_kakao_auth(server_base_url: str, client_id: str) -> str:
        redirect_uri = f"{server_base_url}/auth/kakao/callback"
        return (
            "https://kauth.kakao.com/oauth/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            "&response_type=code"
        )

    @staticmethod
    def callback_kakao_auth(
        code: str,
        server_base_url: str,
        client_id: str,
        client_secret: str,
        login_redirect_url: str,
    ):
        if not code:
            raise HttpError(400, "카카오에서 제공한 코드가 없습니다")

        token_url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": f"{server_base_url}/auth/kakao/callback",
        }

        token_resp = requests.post(token_url, data=data)
        if token_resp.status_code != 200:
            raise HttpError(400, "토큰 교환에 실패했습니다")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HttpError(400, "액세스 토큰을 받지 못했습니다")

        user_info_url = "https://kapi.kakao.com/v2/user/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }

        user_info_resp = requests.get(user_info_url, headers=headers)
        if user_info_resp.status_code != 200:
            raise HttpError(400, "카카오에서 사용자 정보를 가져오는데 실패했습니다")

        user_info = user_info_resp.json()
        kakao_account = user_info.get("kakao_account")
        if not kakao_account:
            raise HttpError(400, "카카오 계정 정보가 없습니다")

        email = kakao_account.get("email")
        if not email:
            raise HttpError(400, "이메일 정보가 없습니다")

        nickname = kakao_account.get("profile", {}).get("nickname", "")

        user = KakaoAuthService.create_or_get_user(email=email, nickname=nickname)
        refresh = RefreshToken.for_user(user)

        return {
            "success": True,
            "message": "카카오 로그인 성공",
            "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
            "user": {"email": user.email},
            "redirect_url": login_redirect_url,
        }


class NaverAuthService:
    @staticmethod
    def create_or_get_user(email: str, nickname: str) -> User:
        user, created = User.objects.get_or_create(
            email=email, defaults={"username": nickname, "is_email_verified": True}
        )

        if created:
            user.first_name = nickname
            user.save()

        return user

    @staticmethod
    def start_naver_auth(server_base_url: str, client_id: str) -> str:
        redirect_uri = f"{server_base_url}/auth/naver/callback"
        return (
            "https://nid.naver.com/oauth2.0/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            "&response_type=code"
            "&state=RANDOM_STATE"  # 보안을 위한 상태 토큰
        )

    @staticmethod
    def callback_naver_auth(
        code: str,
        server_base_url: str,
        client_id: str,
        client_secret: str,
        login_redirect_url: str,
    ):
        if not code:
            raise HttpError(400, "네이버에서 제공한 코드가 없습니다")

        token_url = "https://nid.naver.com/oauth2.0/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "redirect_uri": f"{server_base_url}/auth/naver/callback",
        }

        token_resp = requests.post(token_url, data=data)
        if token_resp.status_code != 200:
            raise HttpError(400, "토큰 교환에 실패했습니다")

        token_data = token_resp.json()
        access_token = token_data.get("access_token")
        if not access_token:
            raise HttpError(400, "액세스 토큰을 받지 못했습니다")

        user_info_url = "https://openapi.naver.com/v1/nid/me"
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        user_info_resp = requests.get(user_info_url, headers=headers)
        if user_info_resp.status_code != 200:
            raise HttpError(400, "네이버에서 사용자 정보를 가져오는데 실패했습니다")

        user_info = user_info_resp.json()
        response = user_info.get("response")
        if not response:
            raise HttpError(400, "네이버 계정 정보가 없습니다")

        email = response.get("email")
        if not email:
            raise HttpError(400, "이메일 정보가 없습니다")

        nickname = response.get("nickname", "")

        user = NaverAuthService.create_or_get_user(email=email, nickname=nickname)
        refresh = RefreshToken.for_user(user)

        return {
            "success": True,
            "message": "네이버 로그인 성공",
            "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
            "user": {"email": user.email},
            "redirect_url": login_redirect_url,
        }
