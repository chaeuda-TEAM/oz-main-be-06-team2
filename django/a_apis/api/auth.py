from typing import Dict

from a_apis.service.auth import GoogleAuthService
from ninja import Router

from django.conf import settings
from django.shortcuts import redirect

router = Router()


@router.get("/google/login/dev")
def google_auth_start_local(request):
    auth_url = GoogleAuthService.start_google_auth(
        settings.SERVER_BASE_URL_DEV, settings.AUTH_GOOGLE_CLIENT_ID
    )
    return redirect(auth_url)


@router.get("/google/callback/dev", response=Dict)
def google_auth_callback_local(request, code: str = None):
    response_data = GoogleAuthService.callback_google_auth(
        code=code,
        server_base_url=settings.SERVER_BASE_URL_DEV,
        client_id=settings.AUTH_GOOGLE_CLIENT_ID,
        client_secret=settings.AUTH_GOOGLE_CLIENT_SECRET,
        login_redirect_url=settings.LOGIN_REDIRECT_URL_DEV,
    )
    return response_data


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
        login_redirect_url=settings.LOGIN_REDIRECT_URL,
    )
