import os
from typing import Optional

import boto3
import requests
from a_apis.models.products import (
    ProductAddress,
    ProductDetail,
    ProductImg,
    ProductVideo,
)
from a_apis.schema.products import (
    ImageSchema,
    ProductAllResponseSchema,
    ProductAllSchema,
    ProductDetailSchema,
    VideoSchema,
)
from dotenv import load_dotenv
from ninja.errors import HttpError

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import UploadedFile
from django.http import JsonResponse

load_dotenv()


# 부동산 매물등록 관련
class ProductService:
    @staticmethod
    def create_product(
        user: User,
        data: ProductAllSchema,
        images: list[UploadedFile],
        video: Optional[UploadedFile],
    ):
        if not user.is_authenticated:
            raise HttpError(401, "로그인이 필요합니다.")

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
                sale=data.detail.sale,
                pro_supply_a=data.detail.pro_supply_a,
                pro_site_a=data.detail.pro_site_a,
                pro_heat=data.detail.pro_heat,
                pro_type=data.detail.pro_type,
                address=product_address,  # 주소 필드 설정
                video=product_video,  # 동영상 필드 설정
            )

            if len(images) > 10:
                raise ValueError("최대 10장의 이미지만 업로드할 수 있습니다.")

            for image in images:
                ProductImg.objects.create(product_detail=product_detail, img_url=image)

            response_data = {
                "images": [default_storage.url(image.name) for image in images],
                "video": default_storage.url(video.name) if video else None,
                "detail": {
                    "pro_title": product_detail.pro_title,
                    "pro_price": product_detail.pro_price,
                    "management_cost": product_detail.management_cost,
                    "pro_supply_a": product_detail.pro_supply_a,
                    "pro_site_a": product_detail.pro_site_a,
                    "pro_heat": product_detail.pro_heat,
                    "pro_type": product_detail.pro_type,
                    "pro_floor": product_detail.pro_floor,
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
                images=response_data["images"],
                video=response_data["video"],
                detail=response_data["detail"],
                address=response_data["address"],
            )

        except ValueError as e:
            raise HttpError(400, f"잘못된 요청: {str(e)}")
        except Exception as e:
            raise HttpError(500, f"데이터 저장 중 오류가 발생했습니다: {str(e)}")
