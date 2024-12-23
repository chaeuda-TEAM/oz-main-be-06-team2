import re

from a_apis.auth.cookies import create_auth_response
from a_apis.models.email_verification import EmailVerification
from a_apis.schema.users import LoginSchema, SignupSchema, WithdrawalSchema
from allauth.account.models import EmailAddress
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model, login
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import IntegrityError

User = get_user_model()


class UserService:
    @staticmethod
    def login_user(request, data: LoginSchema):
        user = authenticate(request, username=data.user_id, password=data.password)
        if user:
            email_address = EmailAddress.objects.filter(user=user, primary=True).first()
            if email_address and email_address.verified:
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
            return {"success": False, "message": "이메일 인증이 필요합니다."}
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
                        "user_id": user.user_id,
                    },
                }
        except Exception as e:
            return {"success": False, "message": str(e)}

    @staticmethod
    def signup(data: SignupSchema):
        try:
            # 이메일 인증 코드 확인
            verification = EmailVerification.objects.filter(
                email=data.email,
                verification_code=data.code,
            ).exists()

            if not verification:
                raise ValueError("유효하지 않은 이메일 인증 코드입니다.")

            # 비밀번호 확인 검증
            if data.password != data.password_confirm:
                raise ValueError("비밀번호가 일치하지 않습니다.")

            # 이메일 유효성 검사
            try:
                validate_email(data.email)
            except ValidationError:
                raise ValueError("유효하지 않은 이메일 형식입니다.")

            # 비밀번호 복잡성 검사
            if len(data.password) < 8:
                raise ValueError("비밀번호는 최소 8자 이상이어야 합니다.")

            # 전화번호 형식 검사
            phone_pattern = re.compile(r"^01[016789]-?[0-9]{3,4}-?[0-9]{4}$")
            if not phone_pattern.match(data.phone_number):
                raise ValueError("유효하지 않은 전화번호 형식입니다.")

            # 사용자 ID 중복 검사 - 탈퇴한 사용자 확인
            existing_user = User.objects.filter(user_id=data.user_id).first()
            if existing_user:
                if existing_user.is_active:
                    raise ValueError("이미 사용 중인 사용자 ID입니다.")
                else:
                    # 탈퇴한 사용자의 경우 계정 재활성화
                    existing_user.is_active = True
                    existing_user.username = data.username
                    existing_user.email = data.email
                    existing_user.phone_number = data.phone_number
                    existing_user.set_password(data.password)
                    existing_user.save()
                    user = existing_user

            else:
                # 새로운 사용자 생성
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

    @staticmethod
    def find_user_id(username: str, email: str) -> dict:
        try:
            user = User.objects.get(username=username, email=email)

            # 이메일 내용 구성
            subject = "회원님의 아이디를 알려드립니다"
            message = f"""
                안녕하세요, {username}님
                
                회원님의 아이디는 다음과 같습니다:
                {user.user_id}
                
                로그인 페이지에서 위 아이디로 로그인해주세요.
            """
            html_message = f"""
                <html>
                    <body>
                        <h2>회원 아이디 안내</h2>
                        <p>안녕하세요, {username}님</p>
                        <p>회원님의 아이디는 다음과 같습니다:</p>
                        <h3>{user.user_id}</h3>
                        <p>로그인 페이지에서 위 아이디로 로그인해주세요.</p>
                    </body>
                </html>
            """

            # 이메일 전송
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            return {
                "success": True,
                "message": "입력하신 이메일로 아이디를 발송했습니다. 이메일을 확인해주세요.",
            }

        except User.DoesNotExist:
            return {
                "success": False,
                "message": "입력하신 정보와 일���하는 사용자가 없습니다.",
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"처리 중 오류가 발생했습니다: {str(e)}",
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
            if not user.check_password(data.password):
                return {"success": False, "message": "비밀번호가 일치하지 않습니다."}

            # 소프트 딜리트 처리
            user.is_active = False
            user.save()

            # 로그아웃 처리를 위한 토�� 무효화
            RefreshToken.for_user(user)

            return {"success": True, "message": "회원 탈퇴가 완료되었습니다."}

        except Exception as e:
            return {
                "success": False,
                "message": f"회원 탈퇴 처리 중 오류가 발생했습니다: {str(e)}",
            }
