from typing import Optional

from a_apis.auth.bearer import AuthBearer
from a_apis.models import ProductDetail
from a_apis.schema.products import (
    ProductAllResponseSchema,
    ProductAllSchema,
    ProductDetailSchema,
)
from a_apis.service.products import ProductService
from ninja import File, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja.security import django_auth

from django.contrib.auth.decorators import login_required

public_router = Router()
router = Router(auth=AuthBearer())


@router.post("/create", response=ProductAllResponseSchema)
@login_required
def create_product(
    request,
    data: ProductAllSchema,
    images: list[UploadedFile] = File(...),
    video: Optional[UploadedFile] = File(None),
):
    """
    매물 등록 API

    Args:
        request: Django 요청 객체
        data (ProductAllSchema): 생성할 매물의 데이터
        images (list[UploadedFile]): 업로드할 이미지 파일 목록
        video (Optional[UploadedFile]): 업로드할 동영상 파일 (없을 수도 있음)

    Returns:
        ProductAllResponseSchema: 생성된 매물 응답 데이터
    """
    try:
        user = request.user
        response_data = ProductService.create_product(user, data, images, video)
        return response_data
    except HttpError as e:
        return JsonResponse({"success": False, "message": str(e)}, status=e.status_code)
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": "서버 오류가 발생했습니다."}, status=500
        )


@public_router.get("/EUM-CHECK", response=dict)
def eum_check(request):
    """
    EUM 초이스필드 프론트분들 확인용
    """
    return {
        "heat_choices": dict(ProductDetail.HEAT_CHOICES),
        "type_choices": dict(ProductDetail.TYPE_CHOICES),
    }
