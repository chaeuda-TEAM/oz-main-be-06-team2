from a_apis.schema.products import AddressSchema
from a_apis.service.products import AddressService
from ninja import Router
from ninja.errors import HttpError
from ninja.security import django_auth

router = Router()


@router.post("/save-product-address", response=dict)
def save_product_address(request, data: AddressSchema):
    """
    매물 주소 저장 엔드포인트

    Args:
        request: HTTP 요청 객체
        data: 주소 요청 데이터 (AddressSchema)

    Returns:
        dict: 주소 생성 결과
    """
    user = request.user  # 로그인된 유저 정보를 가져옴
    if not user.is_authenticated:
        raise HttpError(401, "로그인이 필요합니다.")

    result = AddressService.save_product_address(user, data)
    return result
