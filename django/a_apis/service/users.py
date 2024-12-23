import re

from a_apis.auth.cookies import create_auth_response
from a_apis.models.email_verification import EmailVerification
from a_apis.schema.users import LoginSchema, SignupSchema
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate, get_user_model, login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError

User = get_user_model()


class UserService:
    @staticmethod
    def login_user(request, data: LoginSchema):
        user = authenticate(request, username=data.user_id, password=data.password)
        if user:
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return {
                "success": True,
                "message": "로그인 되었습니다.",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": {
                    "email": user.email,
                    "username": user.username,
                    "user_id": user.user_id,
                },
            }
        return {"success": False, "message": "아이디 또는 비밀번호가 잘못되었습니다."}

    @staticmethod
    def refresh_token(refresh_token: str):
        try:
            refresh = RefreshToken(refresh_token)
            result = {
                "success": True,
                "message": "토큰이 갱신되었습니다.",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
            }
            return create_auth_response(
                result, result["tokens"]["access"], result["tokens"]["refresh"]
            )
        except TokenError as e:
            return {"success": False, "message": "유효하지 않은 리프레시 토큰입니다."}

    @staticmethod
    def get_user(request):
        try:
            user = request.auth
            if not user:
                return {"success": False, "message": "인증되지 않은 사용자입니다."}

            from rest_framework_simplejwt.tokens import AccessToken

            access_token = AccessToken(user)
            user_id = access_token["user_id"]

            user = User.objects.get(id=user_id)

            return {
                "success": True,
                "message": "인증된 사용자입니다.",
                "user": {"email": user.email},
            }
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def signup(data: SignupSchema):
        try:
            # 이메일 인증 확인
            verification = EmailVerification.objects.filter(
                email=data.email, is_verified=True
            ).exists()

            if not verification:
                raise ValueError("이메일 인증이 필요합니다.")

            # 비밀번호 확인 검증
            if data.password != data.password_confirm:
                raise ValueError("비밀번호가 일치하지 않습니다.")

            # 이메일 유효성 검사
            try:
                validate_email(data.email)
            except ValidationError:
                raise ValueError("유효하지 않은 이메일 형식입니다.")

            # 사용자 ID 중복 검사
            if User.objects.filter(user_id=data.user_id).exists():
                raise ValueError("이미 사용 중인 사용자 ID입니다.")

            # 이메일 중복 검사
            if User.objects.filter(email=data.email).exists():
                raise ValueError("이미 사용 중인 이메일입니다.")

            # 비밀번호 복잡성 검사
            if len(data.password) < 8:
                raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

            # 전화번호 형식 검사
            phone_pattern = re.compile(r"^01[016789]-?[0-9]{3,4}-?[0-9]{4}$")
            if not phone_pattern.match(data.phone_number):
                raise ValueError("유효하지 않은 전화번호 형식입니다.")

            # 사용자 생성
            user = User.objects.create_user(
                username=data.username,
                user_id=data.user_id,
                email=data.email,
                password=data.password,
                phone_number=data.phone_number,
                is_email_verified=True,
            )

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)

            return {
                "success": True,
                "message": "회원가입이 완료되었습니다.",
                "tokens": {
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                "user": {
                    "email": user.email,
                    "username": user.username,
                    "user_id": user.user_id,
                },
            }
        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {
                "success": False,
                "message": "회원가입 처리 중 오류가 발생했습니다.",
            }
