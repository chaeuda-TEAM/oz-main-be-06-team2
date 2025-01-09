import logging
from typing import List, Optional

from a_apis.auth.bearer import AuthBearer
from a_apis.models import ProductDetail
from a_apis.schema.products import (
    ProductRequestBodySchema,  # ProductAllSchema -> ProductRequestBodySchema로 변경
)
from a_apis.schema.products import (
    MyProductsSchemaResponseSchema,
    ProductAllResponseSchema,
    ProductLikeResponseSchema,
    ProductUpdateResponseSchema,
    UserLikedProductsResponseSchema,
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
    data: ProductRequestBodySchema,
    images: list[UploadedFile] = File(...),
    video: Optional[UploadedFile] = File(None),
):
    """
    매물 등록 API
    ```
    Args:
        request: Django 요청 객체
        data (ProductRequestBodySchema): 생성할 매물의 데이터
        images (list[UploadedFile]): 업로드할 이미지 파일 목록 (최대 10장)
        video (Optional[UploadedFile]): 업로드할 동영상 파일 (선택사항)

    Returns:
        ProductAllResponseSchema: 생성된 매물 응답 데이터
        - success: bool (생성 성공 여부)
        - message: str (응답 메시지)
        - product: ProductResponseDetailSchema
            - product_id: int (매물 ID)
            - images: list[str] (이미지 URL 목록)
            - video: Optional[str] (동영상 URL)
            - pro_title: str (매물 제목)
            - ... (기타 매물 상세 정보)
            - created_at: datetime (등록일)
            - updated_at: datetime (수정일)

    Note:
        - management_cost: Optional[int] - 관리비가 있는 경우에만 포함
        - sale: Optional[bool] - 기본값 True
    ```
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
    data: ProductRequestBodySchema,
    images: list[UploadedFile] = File(None),
    video: Optional[UploadedFile] = File(None),
):
    """
    매물 수정 API
    ```
    Args:
        request: Django 요청 객체
        product_id (int): 수정할 매물 ID
        data (ProductRequestBodySchema): 수정할 매물 데이터
        images (list[UploadedFile]): 새로 업로드할 이미지 파일 목록 (선택사항)
        video (Optional[UploadedFile]): 새로 업로드할 동영상 파일 (선택사항)

    Returns:
        ProductUpdateResponseSchema: 수정된 매물 응답 데이터
        - success: bool (수정 성공 여부)
        - message: str (응답 메시지)
        - product: ProductUpdateResponseDetailSchema
            - product_id: int (매물 ID)
            - images: list[str] (이미지 URL 목록)
            - video: Optional[str] (동영상 URL)
            - pro_title: str (매물 제목)
            - ... (기타 매물 상세 정보)
            - created_at: datetime (등록일)
            - updated_at: datetime (수정일)

    Note:
        - management_cost: Optional[int] - 관리비가 있는 경우에만 포함
        - sale: Optional[bool] - 기본값 True
        - images나 video를 제공하지 않으면 기존 파일 유지
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


@router.get("/like-mylist", response=UserLikedProductsResponseSchema)
@login_required
def mylist_like_products(request):
    """
    사용자가 찜한 매물 목록 조회 API
    ```
    Args:
        request: Django 요청 객체

    Returns:
        UserLikedProductsResponseSchema: 찜한 매물 목록 조회 결과
        - success: bool (요청 처리 성공 여부)
        - message: str (응답 메시지)
        - total_count: int (전체 찜한 매물 수)
        - products: list[UserLikedProductsSchema] (찜한 매물 목록)
            - product_id: int (매물 ID)
            - pro_title: str (매물 제목)
            - pro_price: int (매물 가격)
            - pro_type: str (건물 유형)
            - pro_supply_a: float (공급면적)
            - add_new: str (매물 도로명주소)
            - images: Optional[str] (매물 대표 이미지 URL -첫 번째 이미지 사용)
            - created_at: datetime (찜한 시간)
    ```
    """
    try:
        response_data = ProductService.mylist_like_products(request.user)
        return response_data
    except HttpError as e:
        return Response({"success": False, "message": str(e)}, status=e.status_code)
    except Exception as e:
        return Response(
            {"success": False, "message": "서버 오류가 발생했습니다."}, status=500
        )


@router.get("/products-mylist", response=MyProductsSchemaResponseSchema)
@login_required
def mylist_products(request):
    """
    사용자가 등록한 매물 목록 조회 API
    ```
    Args:
        request: Django 요청 객체

    Returns:
        MyProductsSchemaResponseSchema: 등록한 매물 목록 조회 결과
        - success: bool (요청 처리 성공 여부)
        - message: str (응답 메시지)
        - total_count: int (전체 등록 매물 수)
        - products: list[MyProductsSchema] (등록한 매물 목록)
            - product_id: int (매물 ID)
            - pro_title: str (매물 제목)
            - pro_price: int (매물 가격)
            - pro_type: str (건물 유형)
            - pro_supply_a: float (공급면적)
            - add_new: str (매물 도로명주소)
            - images: Optional[str] (매물 대표 이미지 URL - 첫번째 이미지 사용)
            - created_at: datetime (등록 시간)
    ```
    """
    try:
        response_data = ProductService.mylist_products(request.user)
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
