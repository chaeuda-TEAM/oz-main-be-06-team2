from ninja.security import HttpBearer
from rest_framework_simplejwt.tokens import AccessToken

from django.contrib.auth import get_user_model

User = get_user_model()


class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        try:
            access_token = AccessToken(token)
            user = User.objects.get(id=access_token["user_id"])
            request.user = user
            return token
        except Exception:
            return None
