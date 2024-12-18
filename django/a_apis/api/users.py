from a_apis.auth.bearer import AuthBearer
from a_apis.auth.cookies import create_auth_response
from a_apis.schema.users import *
from a_apis.service.users import UserService
from ninja import Router

router = Router(auth=AuthBearer())


@router.get("/me", response=AuthResponseSchema)
def get_user(request):
    return UserService.get_user(request)


@router.post("/refresh", response=TokenResponseSchema)
def refresh_token(request, data: RefreshTokenSchema):
    return UserService.refresh_token(data.refresh)
