from a_apis.auth.bearer import AuthBearer
from a_apis.schema.users import *
from a_apis.service.email import EmailService
from a_apis.service.users import UserService
from ninja import Router

nomal_router = Router()
router = Router(auth=AuthBearer())


@nomal_router.post("/login", response=AuthResponseSchema)
def login(request, data: LoginSchema):
    """
    로그인 엔드포인트

    Args:
        request: HTTP 요청 객체
        data: 로그인 데이터 (LoginSchema)

    Returns:
        AuthResponseSchema: 로그인 결과 및 토큰 정보
    """
    return UserService.login_user(request, data)


@nomal_router.post("/signup", response=AuthResponseSchema)
def signup(request, data: SignupSchema):
    """
    회원가입 엔드포인트

    Args:
        request: HTTP 요청 객체
        data: 회원가입 데이터 (SignupSchema)

    Returns:
        AuthResponseSchema: 회원가입 결과 및 토큰 정보
    """
    return UserService.signup(data)


@router.get("/me", response=AuthResponseSchema)
def get_user(request):
    """
    사용자 정보 조회 엔드포인트

    Args:
        request: HTTP 요청 객체

    Returns:
        AuthResponseSchema: 사용자 정보 및 토큰 정보
    """
    return UserService.get_user(request)


@nomal_router.post("/refresh", response=TokenResponseSchema)
def refresh_token(request, data: RefreshTokenSchema):
    """
    토큰 갱신 엔드포인트

    Args:
        request: HTTP 요청 객체
        data: 토큰 데이터 (RefreshTokenSchema)

    Returns:
        TokenResponseSchema: 토큰 정보
    """
    return UserService.refresh_token(data.refresh)


@nomal_router.post("/request-email-verification", response=dict)
def request_email_verification(request, data: EmailVerificationRequestSchema):
    """
    이메일 인증 요청 엔드포인트

    Args:
        request: HTTP 요청 객체
        data: 이메일 인증 요청 데이터 (EmailVerificationRequestSchema)

    Returns:
        dict: 이메일 인증 요청 결과
    """
    return EmailService.send_verification_email(data.email)


@nomal_router.get("/verify-email", response=dict)
def verify_email(request, code: str):
    """
    이메일 인증 확인 엔드포인트

    Args:
        request: HTTP 요청 객체
        code: 이메일 인증 코드

    Returns:
        dict: 이메일 인증 확인 결과
    """
    return EmailService.verify_email(code)
