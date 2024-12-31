import random
import re
import string

from a_apis.auth.cookies import create_auth_response
from a_apis.models.email_verification import EmailVerification
from a_apis.schema.users import (
    LoginSchema,
    LogoutSchema,
    SignupSchema,
    WithdrawalSchema,
)
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.contrib.auth import authenticate, get_user_model, login
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

User = get_user_model()


class UserService:
    @staticmethod
    def _generate_random_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation
        return "".join(random.choice(characters) for _ in range(length))

    @staticmethod
    def login_user(request, data: LoginSchema):
        try:
            user = User.objects.filter(email=data.email, is_social_login=True).first()
            if user:
                social_types = [
                    su.social_type.upper() for su in user.social_users.all()
                ]
                social_types_str = ", ".join(social_types)
                return {
                    "success": False,
                    "message": f"{social_types_str} 로그인 사용자입니다. 소셜 로그인으로 로그인해주세요.",
                }

            user = authenticate(request, username=data.email, password=data.password)
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
                        "user_id": user.email,
                    },
                }
            return {
                "success": False,
                "message": "이메일 또는 비밀번호가 잘못되었습니다.",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"로그인 처리 중 오류가 발생했습니다: {str(e)}",
            }

    @staticmethod
    def refresh_token(refresh_token: str):
        try:
            # 기존 토큰 검증
            token = RefreshToken(refresh_token)

            # 기존 토큰 블랙리스트에 추가
            token.blacklist()

            # 새로운 토큰 발급
            user = User.objects.get(id=token["user_id"])
            new_refresh = RefreshToken.for_user(user)

            result = {
                "success": True,
                "message": "토큰이 갱신되었습니다.",
                "tokens": {
                    "access": str(new_refresh.access_token),
                    "refresh": str(new_refresh),
                },
            }
            return create_auth_response(
                result, result["tokens"]["access"], result["tokens"]["refresh"]
            )
        except TokenError:
            return {"success": False, "message": "유효하지 않은 리프레시 토큰입니다."}
        except Exception as e:
            return {
                "success": False,
                "message": f"토큰 갱신 중 오류가 발생했습니다: {str(e)}",
            }

    @staticmethod
    def get_user(request):
        try:
            user = request.auth
            if not user:
                return {"success": False, "message": "인증되지 않은 사용자입니다."}

            access_token = AccessToken(user)
            user_id = access_token["user_id"]

            user = User.objects.get(id=user_id)

            refresh = RefreshToken.for_user(user)

            if not user.is_active:
                return {"success": False, "message": "탈퇴한 사용자입니다."}
            else:
                return {
                    "success": True,
                    "message": "인증된 사용자입니다.",
                    "tokens": {
                        "access": str(refresh.access_token),
                        "refresh": str(refresh),
                    },
                    "user": {
                        "email": user.email,
                        "username": user.username,
                    },
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

            # 이메일 유효성 검사
            try:
                validate_email(data.email)
            except ValidationError:
                raise ValueError("유효하지 않은 이메일 형식입니다.")

            # 이메일 중복 검사 수정 - 소프트 딜리트된 계정 제외
            if User.objects.filter(email=data.email, is_active=True).exists():
                raise ValueError("이미 사용 중인 이메일입니다.")

            user = User.objects.filter(email=data.email).first()
            # 비밀번호 복잡성 검사 - 소셜 로그인 사용자는 제외
            if not user or not user.is_social_login:
                if len(data.password) < 6:
                    raise ValueError("비밀번호는 최소 6자 이상이어야 합니다.")

            # 전화번호 형식 검사
            phone_pattern = re.compile(r"^01[016789]-?[0-9]{3,4}-?[0-9]{4}$")
            if not phone_pattern.match(data.phone_number):
                raise ValueError("유효하지 않은 전화번호 형식입니다.")

            # 소프트 딜리트된 계정 확인 및 복구
            deleted_user = User.objects.filter(
                email=data.email, is_active=False
            ).first()

            if deleted_user:
                # 기존 계정 복구
                deleted_user.is_active = True
                deleted_user.username = data.username
                deleted_user.phone_number = data.phone_number
                if user.is_social_login:
                    random_password = UserService._generate_random_password()
                    deleted_user.set_password(random_password)
                else:
                    deleted_user.set_password(data.password)
                deleted_user.is_social_login = user.is_social_login
                deleted_user.save()
                user = deleted_user
            else:
                # 새 사용자 생성
                user_data = {
                    "username": data.username,
                    "email": data.email,
                    "phone_number": data.phone_number,
                    "is_email_verified": True,
                    "is_social_login": user.is_social_login if user else False,
                }

                if user and user.is_social_login:
                    random_password = UserService._generate_random_password()
                    user = User.objects.create_user(
                        **user_data, password=random_password
                    )
                else:
                    user = User.objects.create_user(**user_data, password=data.password)

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)

            # 이메일 인증 데이터 삭제
            EmailVerification.objects.filter(email=data.email).delete()

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
                },
            }
        except ValueError as e:
            return {"success": False, "message": str(e)}
        except Exception as e:
            return {
                "success": False,
                "message": "회원가입 처리 중 오류가 발생했습니다.",
            }

    @staticmethod
    def withdraw_user(request, data: WithdrawalSchema):
        try:
            user = request.auth
            if not user:
                return {"success": False, "message": "인증되지 않은 사용자입니다."}

            access_token = AccessToken(user)
            user_id = access_token["user_id"]

            user = User.objects.get(id=user_id)

            # 인증되지 않은 사용자 체크
            if not user.is_authenticated:
                return {"success": False, "message": "인증되지 않은 사용자입니다."}

            # 비밀번호 확인
            if not user.is_social_login:
                if not user.check_password(data.password):
                    return {
                        "success": False,
                        "message": "비밀번호가 일치하지 않습니다.",
                    }

            # 소프트 딜리트 처리
            user.is_active = False
            user.save()

            # 로그아웃 처리를 위한 토큰 무효화
            RefreshToken.for_user(user)

            return {"success": True, "message": "회원 탈퇴가 완료되었습니다."}

        except Exception as e:
            return {
                "success": False,
                "message": f"회원 탈퇴 처리 중 오류가 발생했습니다: {str(e)}",
            }

    @staticmethod
    def logout_user(data: LogoutSchema):
        try:
            # 리프레시 토큰 검증
            token = RefreshToken(data.refresh_token)

            # 토큰 블랙리스트에 추가
            token.blacklist()

            return {"success": True, "message": "로그아웃 되었습니다."}

        except TokenError:
            return {"success": False, "message": "유효하지 않은 토큰입니다."}
        except Exception as e:
            return {
                "success": False,
                "message": f"로그아웃 처리 중 오류가 발생했습니다: {str(e)}",
            }
