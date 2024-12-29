import os
from typing import Optional

import boto3
import requests
from a_apis.models.products import (
    Cost,
    ProductAddress,
    ProductDetail,
    ProductImg,
    ProductVideo,
)
from a_apis.schema.products import (
    CostSchema,
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


class ProductService:
    @staticmethod
    def create_product(
        user: User,
        data: ProductAllSchema,
        images: list[UploadedFile],
        video: Optional[UploadedFile],
    ):
        try:
            # ProductAddress 객체 생성
            product_address = ProductAddress.objects.create(
                add_new=data.address.add_new,
                add_old=data.address.add_old,
                latitude=data.address.latitude,
                longitude=data.address.longitude,
            )

            # Cost 객체 생성
            cost = Cost.objects.create(
                cost_type=data.cost.cost_type,
                mg_cost=data.cost.mg_cost,
            )

            # ProductDetail 객체 생성
            product_detail = ProductDetail.objects.create(
                user=user,
                pro_title=data.detail.pro_title,
                pro_price=data.detail.pro_price,
                pro_supply_a=data.detail.pro_supply_a,
                pro_site_a=data.detail.pro_site_a,
                pro_heat=data.detail.pro_heat,
                pro_type=data.detail.pro_type,
                address=product_address,  # 주소 필드 설정
                cost=cost,  # 비용 필드 설정
            )

            # 이미지 데이터를 S3에 업로드하고 URL을 DB에 저장
            if len(images) > 15:
                raise ValueError("최대 15장의 이미지만 업로드할 수 있습니다.")

            for image in images:
                ProductImg.objects.create(product_detail=product_detail, img_url=image)

            # 동영상 데이터를 S3에 업로드하고 URL을 DB에 저장
            if video:
                ProductVideo.objects.create(
                    product_detail=product_detail, video_url=video
                )

            response_data = {
                "images": [
                    img.img_url
                    for img in ProductImg.objects.filter(product_detail=product_detail)
                ],
                "video": (
                    ProductVideo.objects.filter(product_detail=product_detail)
                    .first()
                    .video_url
                    if video
                    else None
                ),
                "detail": {
                    "pro_title": product_detail.pro_title,
                    "pro_price": product_detail.pro_price,
                    "pro_supply_a": product_detail.pro_supply_a,
                    "pro_site_a": product_detail.pro_site_a,
                    "pro_heat": product_detail.pro_heat,
                    "pro_type": product_detail.pro_type,
                    "pro_floor": product_detail.pro_floor,
                    "pro_intro": product_detail.pro_intro,
                    "sale": product_detail.sale,
                },
                "cost": {
                    "cost_type": product_detail.cost.cost_type,
                    "mg_cost": product_detail.cost.mg_cost,
                },
                "address": {
                    "add_new": product_detail.address.add_new,
                    "add_old": product_detail.address.add_old,
                    "latitude": product_detail.address.latitude,
                    "longitude": product_detail.address.longitude,
                },
            }

            return ProductAllResponseSchema(
                success=True, message="성공적으로 생성되었습니다.", data=response_data
            )

        except Exception as e:
            raise HttpError(500, f"데이터 저장 중 오류가 발생했습니다: {str(e)}")
