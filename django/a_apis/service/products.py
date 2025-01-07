import os
import uuid
from typing import Optional

from a_apis.models.products import (
    ProductAddress,
    ProductDetail,
    ProductImg,
    ProductLikes,
    ProductVideo,
)
from a_apis.schema.products import (
    ProductAllResponseSchema,
    ProductAllSchema,
    ProductLikeResponseSchema,
    ProductUpdateResponseSchema,
    UserLikedProductsResponseSchema,
    UserLikedProductsSchema,
)
from dotenv import load_dotenv
from ninja.errors import HttpError
from ninja.responses import Response

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.db import transaction

load_dotenv()


# 매물 관련 서비스
class ProductService:
    # 매물 등록
    @staticmethod
    def create_product(
        user: User,
        data: ProductAllSchema,
        images: list[UploadedFile],
        video: Optional[UploadedFile],
    ):
        if not user.is_authenticated:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."}, status=401
            )

        try:
            # ProductAddress 객체 생성
            product_address = ProductAddress.objects.create(
                add_new=data.address.add_new,
                add_old=data.address.add_old,
                latitude=data.address.latitude,
                longitude=data.address.longitude,
            )

            # ProductVideo 객체 생성
            product_video = None
            if video:
                product_video = ProductVideo.objects.create(video_url=video)

            # ProductDetail 객체 생성
            product_detail = ProductDetail.objects.create(
                user=user,
                pro_title=data.detail.pro_title,
                pro_price=data.detail.pro_price,
                management_cost=data.detail.management_cost,
                pro_floor=data.detail.pro_floor,
                description=data.detail.description,
                sale=getattr(
                    data.detail, "sale", True
                ),  # getattr이 True를 반환해서 DB에 sale=True로 저장
                pro_supply_a=data.detail.pro_supply_a,
                pro_site_a=data.detail.pro_site_a,
                pro_heat=data.detail.pro_heat,
                pro_type=data.detail.pro_type,
                pro_rooms=data.detail.pro_rooms,
                pro_bathrooms=data.detail.pro_bathrooms,
                pro_construction_year=data.detail.pro_construction_year,
                address=product_address,  # 주소 필드 설정
                video=product_video,  # 동영상 필드 설정
            )

            if len(images) > 10:
                raise ValueError("최대 10장의 이미지만 업로드할 수 있습니다.")

            image_urls = []
            for image in images:
                # S3에 파일 업로드
                file_extension = image.name.split(".")[-1]
                file_path = f"products/images/{str(uuid.uuid4())[:8]}.{file_extension}"
                saved_path = default_storage.save(file_path, image)
                image_url = default_storage.url(saved_path)
                image_urls.append(image_url)
                ProductImg.objects.create(
                    product_detail=product_detail, img_url=image_url
                )

            # 비디오 처리
            video_url = None
            if video:
                file_path = f"products/videos/{video.name}"
                saved_path = default_storage.save(file_path, video)
                video_url = default_storage.url(saved_path)
                product_video = ProductVideo.objects.create(video_url=video_url)

            response_data = {
                "images": image_urls,
                "video": video_url,
                "detail": {
                    "pro_title": product_detail.pro_title,
                    "pro_price": product_detail.pro_price,
                    "management_cost": product_detail.management_cost,
                    "pro_supply_a": product_detail.pro_supply_a,
                    "pro_site_a": product_detail.pro_site_a,
                    "pro_heat": product_detail.pro_heat,
                    "pro_type": product_detail.pro_type,
                    "pro_floor": product_detail.pro_floor,
                    "pro_rooms": product_detail.pro_rooms,
                    "pro_bathrooms": product_detail.pro_bathrooms,
                    "pro_construction_year": product_detail.pro_construction_year,
                    "description": product_detail.description,
                    "sale": product_detail.sale,
                },
                "address": {
                    "add_new": product_detail.address.add_new,
                    "add_old": product_detail.address.add_old,
                    "latitude": product_detail.address.latitude,
                    "longitude": product_detail.address.longitude,
                },
            }

            return ProductAllResponseSchema(
                success=True,
                message="성공적으로 생성되었습니다.",
                product_id=product_detail.id,
                images=response_data["images"],
                video=response_data["video"],
                detail=response_data["detail"],
                address=response_data["address"],
            )

        except ValueError as e:
            return Response(
                {"success": False, "message": f"잘못된 요청: {str(e)}"}, status=400
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"데이터 저장 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )

    # 매물 수정
    @staticmethod
    def update_product(
        user: User,
        product_id: int,
        data: ProductAllSchema,
        images: Optional[list[UploadedFile]],
        video: Optional[UploadedFile],
    ):
        if not user.is_authenticated:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."}, status=401
            )

        try:
            # 매물 존재 여부와 권한 체크를 분리
            try:
                product_detail = ProductDetail.objects.get(id=product_id)
                if product_detail.user != user:
                    return Response(
                        {
                            "success": False,
                            "message": "해당 매물을 수정할 권한이 없습니다.",
                        },
                        status=403,
                    )
            except ProductDetail.DoesNotExist:
                return Response(
                    {"success": False, "message": "매물을 찾을 수 없습니다."},
                    status=404,
                )

            with transaction.atomic():
                # 주소 정보 업데이트
                product_detail.address.add_new = data.address.add_new
                product_detail.address.add_old = data.address.add_old
                product_detail.address.latitude = data.address.latitude
                product_detail.address.longitude = data.address.longitude
                product_detail.address.save()

                # 비디오 처리 - 새 비디오가 제공된 경우에만 업데이트
                if video:
                    if product_detail.video:
                        old_video = product_detail.video
                        # S3에 새 비디오 업로드
                        file_path = f"products/videos/{video.name}"
                        saved_path = default_storage.save(file_path, video)
                        video_url = default_storage.url(saved_path)
                        product_detail.video = ProductVideo.objects.create(
                            video_url=video_url
                        )
                        old_video.delete()

                # 기본 정보 업데이트
                product_detail.pro_title = data.detail.pro_title
                product_detail.pro_price = data.detail.pro_price
                product_detail.management_cost = data.detail.management_cost
                product_detail.pro_floor = data.detail.pro_floor
                product_detail.description = data.detail.description
                product_detail.sale = getattr(data.detail, "sale", True)
                product_detail.pro_supply_a = data.detail.pro_supply_a
                product_detail.pro_site_a = data.detail.pro_site_a
                product_detail.pro_heat = data.detail.pro_heat
                product_detail.pro_type = data.detail.pro_type
                product_detail.pro_rooms = data.detail.pro_rooms
                product_detail.pro_bathrooms = data.detail.pro_bathrooms
                product_detail.pro_construction_year = data.detail.pro_construction_year
                product_detail.save()

                # 이미지 처리 - 새 이미지가 제공된 경우에만 업데이트
                if images:
                    old_images = list(product_detail.product_images.all())
                    ProductImg.objects.filter(product_detail=product_detail).delete()

                    image_urls = []
                    for image in images:
                        # S3에 새 이미지 업로드
                        file_extension = image.name.split(".")[-1]
                        file_path = (
                            f"products/images/{str(uuid.uuid4())[:8]}.{file_extension}"
                        )
                        saved_path = default_storage.save(file_path, image)
                        image_url = default_storage.url(saved_path)
                        image_urls.append(image_url)
                        ProductImg.objects.create(
                            product_detail=product_detail, img_url=image_url
                        )

                # response_data 구성
                response_data = {
                    "images": (
                        [
                            default_storage.url(img.img_url.name)
                            for img in product_detail.product_images.all()
                        ]
                        if product_detail.product_images.exists()
                        else None
                    ),
                    "video": (
                        default_storage.url(product_detail.video.video_url.name)
                        if product_detail.video
                        else None
                    ),
                    "detail": {
                        "pro_title": product_detail.pro_title,
                        "pro_price": product_detail.pro_price,
                        "management_cost": product_detail.management_cost,
                        "pro_supply_a": product_detail.pro_supply_a,
                        "pro_site_a": product_detail.pro_site_a,
                        "pro_heat": product_detail.pro_heat,
                        "pro_type": product_detail.pro_type,
                        "pro_floor": product_detail.pro_floor,
                        "pro_rooms": product_detail.pro_rooms,
                        "pro_bathrooms": product_detail.pro_bathrooms,
                        "pro_construction_year": product_detail.pro_construction_year,
                        "description": product_detail.description,
                        "sale": product_detail.sale,
                    },
                    "address": {
                        "add_new": product_detail.address.add_new,
                        "add_old": product_detail.address.add_old,
                        "latitude": product_detail.address.latitude,
                        "longitude": product_detail.address.longitude,
                    },
                    "product_id": product_detail.id,  # product_id 추가
                }

                return ProductUpdateResponseSchema(
                    success=True,
                    message="성공적으로 수정되었습니다.",
                    product_id=product_detail.id,
                    images=response_data["images"],
                    video=response_data["video"],
                    detail=response_data["detail"],
                    address=response_data["address"],
                )

        except ValueError as e:
            return Response(
                {"success": False, "message": f"잘못된 요청: {str(e)}"}, status=400
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"데이터 수정 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )

    # 매물 찜하기/취소 서비스
    @staticmethod
    def toggle_like_product(user: User, product_id: int):
        if not user.is_authenticated:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."}, status=401
            )

        try:
            product = ProductDetail.objects.get(id=product_id)

            # 이미 찜한 경우 -> 찜하기 취소
            if product.likes.filter(id=user.id).exists():
                product.likes.remove(user)
                is_liked = False
                message = "찜하기가 취소되었습니다."
                created_at = None
            # 찜하지 않은 경우 -> 찜하기
            else:
                product.likes.add(user)
                is_liked = True
                message = "찜하기가 완료되었습니다."
                like_obj = ProductLikes.objects.get(user=user, product=product)
                created_at = like_obj.created_at

            return ProductLikeResponseSchema(
                success=True,
                message=message,
                is_liked=is_liked,
                created_at=created_at,
            )

        except ProductDetail.DoesNotExist:
            return Response(
                {"success": False, "message": "매물을 찾을 수 없습니다."}, status=404
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"찜하기 처리 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )

    # 사용자가 찜한 매물 목록 조회
    @staticmethod
    def mylist_like_products(user):
        if not user.is_authenticated:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."}, status=401
            )

        try:
            liked_products = (
                ProductLikes.objects.filter(user=user)
                .select_related("product", "product__address")
                .prefetch_related("product__product_images")
                .order_by("-created_at")
            )

            products_data = []
            for like in liked_products:
                # 첫 번째 이미지를 가져오기
                first_image = like.product.product_images.first()
                image_url = first_image.img_url if first_image else None

                product_data = UserLikedProductsSchema(
                    product_id=like.product.id,
                    pro_title=like.product.pro_title,
                    pro_price=like.product.pro_price,
                    pro_address=like.product.address.add_new,
                    pro_type=like.product.pro_type,
                    pro_supply_a=like.product.pro_supply_a,
                    image_url=image_url,
                    created_at=like.created_at,
                )
                products_data.append(product_data)

            return UserLikedProductsResponseSchema(
                success=True,
                message="찜한 매물 목록을 성공적으로 조회했습니다.",
                total_count=len(products_data),
                products=products_data,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"찜한 매물 목록 조회 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )
