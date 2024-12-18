import requests
from a_apis.auth.cookies import create_auth_response
from ninja.errors import HttpError
from rest_framework_simplejwt.tokens import RefreshToken

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
        redirect_uri = f"{server_base_url}/api/auth/google/callback"
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
        code: str, server_base_url: str, client_id: str, client_secret: str
    ):
        if not code:
            raise HttpError(400, "No code provided by Google")

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": f"{server_base_url}/api/auth/google/callback",
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
        if not email:
            raise HttpError(400, "No email in user info")

        name = user_info.get("name", "")

        user = GoogleAuthService.create_or_get_user(email=email, name=name)
        refresh = RefreshToken.for_user(user)

        response_data = {
            "success": True,
            "message": "Google 로그인 성공",
            "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
            "user": {"email": user.email},
        }

        return create_auth_response(
            response_data, str(refresh.access_token), str(refresh)
        )
