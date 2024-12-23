from a_apis.auth.bearer import AuthBearer
from a_apis.auth.cookies import create_auth_response
from a_apis.schema.users import *
from a_apis.service.users import UserService
from ninja import Router

router = Router(auth=AuthBearer())


@router.post("/signup", response=AuthResponseSchema)
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
    return UserService.get_user(request)


@router.post("/refresh", response=TokenResponseSchema)
def refresh_token(request, data: RefreshTokenSchema):
    return UserService.refresh_token(data.refresh)
