import logging
from typing import Optional

from a_apis.auth.bearer import AuthBearer
from a_apis.models import ProductDetail
from a_apis.schema.products import (
    ProductAllResponseSchema,
    ProductAllSchema,
    ProductLikeResponseSchema,
    ProductUpdateResponseSchema,
)
from a_apis.service.products import ProductService
from ninja import Body, File, Router
from ninja.errors import HttpError
from ninja.files import UploadedFile
from ninja.responses import Response
from ninja.security import django_auth

from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

router = Router(auth=AuthBearer())
public_router = Router()


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
    ```
    Note:
        - management_cost: 관리비가 있는 경우에만 포함, 없는 경우 필드 자체를 생략하면 null로 저장
        - sale: 항상 true로 저장되므로 요청 시 생략 가능
        ```

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
        return Response({"success": False, "message": str(e)}, status=e.status_code)
    except Exception as e:
        return Response(
            {"success": False, "message": "서버 오류가 발생했습니다."}, status=500
        )


@router.put("/update/{product_id}", response=ProductUpdateResponseSchema)
@login_required
def update_product(
    request,
    product_id: int,
    data: ProductAllSchema,
    images: list[UploadedFile] = File(None),
    video: Optional[UploadedFile] = File(None),
):
    """
    매물 수정 API
    ```
     Note:
        - management_cost: 관리비가 있는 경우에만 포함, 없는 경우 필드 자체를 생략하면 null로 저장
        - sale: 항상 true로 저장되므로 요청 시 생략 가능
    ```
    """
    try:
        user = request.user
        response_data = ProductService.update_product(
            user, product_id, data, images, video
        )
        return response_data

    except HttpError as e:
        return Response({"success": False, "message": str(e)}, status=e.status_code)
    except Exception as e:
        return Response(
            {"success": False, "message": "서버 오류가 발생했습니다."}, status=500
        )


@router.post("/like/{product_id}", response=ProductLikeResponseSchema)
@login_required
def toggle_like_product(
    request,
    product_id: int,
):
    """
    매물 찜하기/취소 API
    ```
    Args:
        request: Django 요청 객체
        product_id (int): 찜하기/취소할 매물 ID

    Returns:
        ProductLikeResponseSchema: 찜하기 처리 결과
        - success: 처리 성공 여부
        - message: 처리 결과 메시지
        - is_liked: 찜하기 상태 (True: 찜 완료, False: 찜 취소)
        - created_at: 찜하기 생성 시간 (찜하기인 경우에만 포함 / 취소하면 null 반환)
    ```
    """
    try:
        user = request.user
        response_data = ProductService.toggle_like_product(user, product_id)
        return response_data

    except HttpError as e:
        return Response({"success": False, "message": str(e)}, status=e.status_code)
    except Exception as e:
        return Response(
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
