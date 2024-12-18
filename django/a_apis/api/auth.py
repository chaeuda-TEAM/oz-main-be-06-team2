from typing import Dict

from a_apis.service.auth import GoogleAuthService
from ninja import Router

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect

router = Router()


@router.get("/google/login")
def google_auth_start(request):
    auth_url = GoogleAuthService.start_google_auth(
        settings.SERVER_BASE_URL, settings.AUTH_GOOGLE_CLIENT_ID
    )
    return redirect(auth_url)


@router.get("/google/callback", response=Dict)
def google_auth_callback(request, code: str = None):
    return GoogleAuthService.callback_google_auth(
        code=code,
        server_base_url=settings.SERVER_BASE_URL,
        client_id=settings.AUTH_GOOGLE_CLIENT_ID,
        client_secret=settings.AUTH_GOOGLE_CLIENT_SECRET,
    )
