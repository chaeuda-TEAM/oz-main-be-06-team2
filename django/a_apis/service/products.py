import os
import uuid
from math import cos, radians
from typing import Optional

from a_apis.models.products import (
    ProductAddress,
    ProductDetail,
    ProductImg,
    ProductLikes,
    ProductVideo,
)
from a_apis.schema.products import (
    MyProductsSchema,
    MyProductsSchemaResponseSchema,
    ProductAllResponseSchema,
    ProductDeleteResponseSchema,
    ProductDetailAllResponseSchema,
    ProductInformationResponseSchema,
    ProductLikeResponseSchema,
    ProductRequestBodySchema,
    ProductResponseDetailSchema,
    ProductUpdateResponseDetailSchema,
    ProductUpdateResponseSchema,
    UserDetailSchema,
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
        data: ProductRequestBodySchema,
        images: list[UploadedFile],
        video: Optional[UploadedFile],
    ):
        if not user.is_authenticated:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."}, status=401
            )

        try:
            if len(images) > 10:
                raise ValueError("최대 10장의 이미지만 업로드할 수 있습니다.")

            # ProductAddress 객체 생성
            product_address = ProductAddress.objects.create(
                add_new=data.add_new,
                add_old=data.add_old,
                latitude=data.latitude,
                longitude=data.longitude,
            )

            # ProductVideo 객체 생성
            product_video = None
            if video:
                product_video = ProductVideo.objects.create(video_url=video)

            # ProductDetail 객체 생성
            product_detail = ProductDetail.objects.create(
                user=user,
                pro_title=data.pro_title,
                pro_price=data.pro_price,
                management_cost=data.management_cost,
                pro_floor=data.pro_floor,
                description=data.description,
                sale=getattr(
                    data, "sale", True
                ),  # getattr이 True를 반환해서 DB에 sale=True로 저장
                pro_supply_a=data.pro_supply_a,
                pro_site_a=data.pro_site_a,
                pro_heat=data.pro_heat,
                pro_type=data.pro_type,
                pro_rooms=data.pro_rooms,
                pro_bathrooms=data.pro_bathrooms,
                pro_construction_year=data.pro_construction_year,
                address=product_address,  # 주소 필드 설정
                video=product_video,  # 동영상 필드 설정
            )

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
                # uuid를 사용하여 고유한 파일명 생성
                file_extension = video.name.split(".")[-1]
                file_path = f"products/videos/{str(uuid.uuid4())[:8]}.{file_extension}"
                saved_path = default_storage.save(file_path, video)
                video_url = default_storage.url(saved_path)
                product_video = ProductVideo.objects.create(video_url=video_url)

            return ProductAllResponseSchema(
                success=True,
                message="성공적으로 생성되었습니다.",
                product=ProductResponseDetailSchema(
                    product_id=product_detail.id,
                    images=image_urls,
                    video=video_url,
                    pro_title=product_detail.pro_title,
                    pro_price=product_detail.pro_price,
                    management_cost=product_detail.management_cost,
                    pro_supply_a=float(product_detail.pro_supply_a),
                    pro_site_a=float(product_detail.pro_site_a),
                    pro_heat=product_detail.pro_heat,
                    pro_type=product_detail.pro_type,
                    pro_floor=product_detail.pro_floor,
                    pro_rooms=product_detail.pro_rooms,
                    pro_bathrooms=product_detail.pro_bathrooms,
                    pro_construction_year=product_detail.pro_construction_year,
                    description=product_detail.description,
                    sale=product_detail.sale,
                    add_new=product_detail.address.add_new,
                    add_old=product_detail.address.add_old,
                    latitude=float(product_detail.address.latitude),
                    longitude=float(product_detail.address.longitude),
                    is_liked=False,  # 생성 시에는 무조건 False
                    created_at=product_detail.created_at,
                    updated_at=product_detail.updated_at,
                ),
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
        data: ProductRequestBodySchema,
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
                product_detail.address.add_new = data.add_new
                product_detail.address.add_old = data.add_old
                product_detail.address.latitude = data.latitude
                product_detail.address.longitude = data.longitude
                product_detail.address.save()

                # 비디오 처리 - 새 비디오가 제공된 경우에만 업데이트
                if video:
                    if product_detail.video:
                        old_video = product_detail.video
                        # uuid를 사용하여 고유한 파일명 생성
                        file_extension = video.name.split(".")[-1]
                        file_path = (
                            f"products/videos/{str(uuid.uuid4())[:8]}.{file_extension}"
                        )
                        saved_path = default_storage.save(file_path, video)
                        video_url = default_storage.url(saved_path)
                        product_detail.video = ProductVideo.objects.create(
                            video_url=video_url
                        )
                        old_video.delete()

                # 기본 정보 업데이트
                product_detail.pro_title = data.pro_title
                product_detail.pro_price = data.pro_price
                product_detail.management_cost = data.management_cost
                product_detail.pro_floor = data.pro_floor
                product_detail.description = data.description
                product_detail.sale = getattr(data, "sale", True)
                product_detail.pro_supply_a = data.pro_supply_a
                product_detail.pro_site_a = data.pro_site_a
                product_detail.pro_heat = data.pro_heat
                product_detail.pro_type = data.pro_type
                product_detail.pro_rooms = data.pro_rooms
                product_detail.pro_bathrooms = data.pro_bathrooms
                product_detail.pro_construction_year = data.pro_construction_year
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

                # 현재 로그인한 사용자의 찜 여부 확인
                # ProductLikes 객체가 없는 경우도 고려
                try:
                    like_obj = ProductLikes.objects.get(
                        user=user, product=product_detail
                    )
                    is_liked = like_obj.is_liked
                except ProductLikes.DoesNotExist:
                    # 찜한 적이 없으면 False
                    is_liked = False

                return ProductUpdateResponseSchema(
                    success=True,
                    message="성공적으로 수정되었습니다.",
                    product=ProductUpdateResponseDetailSchema(
                        product_id=product_detail.id,
                        images=(
                            image_urls
                            if images
                            else [
                                img.img_url.url
                                for img in product_detail.product_images.all()
                            ]
                        ),
                        video=(
                            video_url
                            if video
                            else (
                                product_detail.video.video_url.url
                                if product_detail.video
                                else None
                            )
                        ),
                        pro_title=product_detail.pro_title,
                        pro_price=product_detail.pro_price,
                        management_cost=product_detail.management_cost,
                        pro_supply_a=float(product_detail.pro_supply_a),
                        pro_site_a=float(product_detail.pro_site_a),
                        pro_heat=product_detail.pro_heat,
                        pro_type=product_detail.pro_type,
                        pro_floor=product_detail.pro_floor,
                        pro_rooms=product_detail.pro_rooms,
                        pro_bathrooms=product_detail.pro_bathrooms,
                        pro_construction_year=product_detail.pro_construction_year,
                        description=product_detail.description,
                        sale=product_detail.sale,
                        add_new=product_detail.address.add_new,
                        add_old=product_detail.address.add_old,
                        latitude=float(product_detail.address.latitude),
                        longitude=float(product_detail.address.longitude),
                        is_liked=is_liked,
                        created_at=product_detail.created_at,
                        updated_at=product_detail.updated_at,
                    ),
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
            like_obj, created = ProductLikes.objects.get_or_create(
                user=user, product=product, defaults={"is_liked": True}
            )

            if not created:
                # 이미 존재하는 경우 상태 토글
                like_obj.is_liked = not like_obj.is_liked
                like_obj.save()

            return ProductLikeResponseSchema(
                success=True,
                message=(
                    "찜하기가 완료되었습니다."
                    if like_obj.is_liked
                    else "찜하기가 취소되었습니다."
                ),
                is_liked=like_obj.is_liked,
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
                ProductLikes.objects.filter(
                    user=user,
                    product__is_deleted=False,  # 삭제되지 않은 매물만
                    is_liked=True,  # 실제 찜한 상태인 것만 조회
                )
                .select_related("product", "product__address")
                .prefetch_related("product__product_images")
                .order_by("-created_at")
            )

            # 찜한 매물이 없는 경우도 정상 응답
            if not liked_products.exists():
                return Response(
                    {
                        "success": True,
                        "message": "찜한 매물이 없습니다.",
                        "total_count": 0,
                        "products": [],
                    },
                    status=200,
                )

            products_data = []
            for like in liked_products:
                # 첫 번째 이미지를 가져오기
                first_image = like.product.product_images.first()
                image_url = str(first_image.img_url) if first_image else None

                # 찜 목록이므로 무조건 True (자신이 찜한 목록)
                product_data = UserLikedProductsSchema(
                    product_id=like.product.id,
                    pro_title=like.product.pro_title,
                    pro_price=like.product.pro_price,
                    add_new=like.product.address.add_new,
                    pro_type=like.product.pro_type,
                    pro_supply_a=like.product.pro_supply_a,
                    images=image_url,
                    is_liked=True,  # 본인의 찜 목록이므로 항상 True
                    is_deleted=like.product.is_deleted,
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

    @staticmethod
    # 사용자가 등록한 매물 목록 조회
    def mylist_products(user):
        if not user.is_authenticated:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."}, status=401
            )

        try:
            registered_products = (
                ProductDetail.objects.filter(
                    user=user,
                    is_deleted=False,  # 삭제되지 않은 매물만
                )
                .select_related("address")
                .prefetch_related("product_images")
                .order_by("-created_at")
            )

            if not registered_products.exists():
                return Response(
                    {
                        "success": True,
                        "message": "등록한 매물이 없습니다.",
                        "total_count": 0,
                        "products": [],
                    },
                    status=200,
                )

            products_data = []
            for product_detail in registered_products:
                # 첫 번째 이미지를 가져오기
                first_image = product_detail.product_images.first()
                image_url = str(first_image.img_url) if first_image else None

                # 현재 로그인한 사용자(본인)의 찜 여부 확인
                is_liked = (
                    ProductLikes.objects.filter(
                        user=user, product=product_detail, is_liked=True
                    ).exists()
                    if user.is_authenticated
                    else False
                )

                product_data = MyProductsSchema(
                    product_id=product_detail.id,
                    pro_title=product_detail.pro_title,
                    pro_price=product_detail.pro_price,
                    pro_type=product_detail.pro_type,
                    pro_supply_a=float(product_detail.pro_supply_a),
                    add_new=product_detail.address.add_new,
                    latitude=float(product_detail.address.latitude),
                    longitude=float(product_detail.address.longitude),
                    images=image_url,
                    is_liked=is_liked,
                    is_deleted=product_detail.is_deleted,
                    created_at=product_detail.created_at,
                )
                products_data.append(product_data)

            return MyProductsSchemaResponseSchema(
                success=True,
                message="등록한 매물 목록을 성공적으로 조회했습니다.",
                total_count=len(products_data),
                products=products_data,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"매물 목록 조회 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )

    @staticmethod
    # 매물 상세 조회
    def get_product_detail(user, product_id: int):
        try:
            print(
                f"Service user: {user}, is_authenticated: {user.is_authenticated if user else False}"
            )
            # select_related와 prefetch_related를 사용하여 쿼리 최적화
            product = (
                ProductDetail.objects.filter(is_deleted=False)  # 삭제되지 않은 매물만
                .select_related("user", "address", "video")
                .prefetch_related("product_images", "likes")  # likes 추가
                .get(id=product_id)
            )

            # 이미지 URL 리스트 생성 - str()로 단순 변환
            image_urls = [str(img.img_url) for img in product.product_images.all()]

            # 비디오 URL - default_storage.url()을 사용하여 전체 URL 생성
            video_url = (
                default_storage.url(product.video.video_url.name)
                if product.video
                else None
            )

            # 찜 여부 체크 로직 수정
            is_liked = False
            if user and user.is_authenticated:
                is_liked = ProductLikes.objects.filter(
                    user=user, product=product, is_liked=True
                ).exists()

            # response 구성 부분은 동일
            return ProductDetailAllResponseSchema(
                success=True,
                message="매물 상세 정보를 성공적으로 조회했습니다.",
                product=ProductInformationResponseSchema(
                    product_id=product.id,
                    user=UserDetailSchema(
                        email=product.user.email,
                        username=product.user.username,
                        phone_number=product.user.phone_number,
                    ),
                    images=image_urls,
                    video=video_url,
                    pro_title=product.pro_title,
                    pro_price=product.pro_price,
                    management_cost=product.management_cost,
                    pro_supply_a=float(product.pro_supply_a),
                    pro_site_a=float(product.pro_site_a),
                    pro_heat=product.pro_heat,
                    pro_type=product.pro_type,
                    pro_floor=product.pro_floor,
                    description=product.description,
                    sale=product.sale,
                    pro_rooms=product.pro_rooms,
                    pro_bathrooms=product.pro_bathrooms,
                    pro_construction_year=product.pro_construction_year,
                    add_new=product.address.add_new,
                    add_old=product.address.add_old,
                    latitude=float(product.address.latitude),
                    longitude=float(product.address.longitude),
                    is_liked=is_liked,
                    is_deleted=product.is_deleted,
                    created_at=product.created_at,
                    updated_at=product.updated_at,
                ),
            )

        except ProductDetail.DoesNotExist:
            return Response(
                {"success": False, "message": "매물을 찾을 수 없습니다."}, status=404
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"매물 상세 정보 조회 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )

    @staticmethod
    # 지도 주변 매물 조회
    def get_nearby_products(
        user: Optional[User], latitude: float, longitude: float, zoom: int
    ):
        try:
            # 줌 레벨에 따른 검색 반경 설정 (km)
            # 9: ~300km (광역권)
            # 13: ~20km (시/군 단위)
            # 16: ~2km (동/읍 단위)
            # 19: ~0.1km (건물 단위)
            distance_map = {
                9: 300.0,  # 광역권
                10: 200.0,
                11: 100.0,
                12: 50.0,
                13: 20.0,  # 광역시 기준 여러 구 단위
                14: 10.0,
                15: 5.0,
                16: 2.0,  # 동/읍 단위
                17: 1.0,
                18: 0.5,
                19: 0.1,  # 건물 단위
            }

            distance = distance_map[zoom]

            # 위도/경도 범위 계산 (근사값)
            lat_range = distance / 111.0
            lon_range = distance / (111.0 * cos(radians(latitude)))

            # 주어진 범위 내의 매물 조회
            nearby_products = (
                ProductDetail.objects.filter(
                    is_deleted=False,  # 삭제되지 않은 매물만
                    address__latitude__range=(
                        latitude - lat_range,
                        latitude + lat_range,
                    ),
                    address__longitude__range=(
                        longitude - lon_range,
                        longitude + lon_range,
                    ),
                    sale=True,  # 판매 중인 매물만 조회
                )
                .select_related("address")
                .prefetch_related("product_images", "likes")
                .order_by("-created_at")
            )

            products_data = []
            for product in nearby_products:
                # 첫 번째 이미지 가져오기
                first_image = product.product_images.first()
                image_url = str(first_image.img_url) if first_image else None

                # 찜 여부 확인
                is_liked = False
                if user and user.is_authenticated:
                    is_liked = ProductLikes.objects.filter(
                        user=user, product=product, is_liked=True
                    ).exists()

                product_data = MyProductsSchema(
                    product_id=product.id,
                    pro_title=product.pro_title,
                    pro_price=product.pro_price,
                    pro_type=product.pro_type,
                    pro_supply_a=float(product.pro_supply_a),
                    add_new=product.address.add_new,
                    latitude=float(product.address.latitude),
                    longitude=float(product.address.longitude),
                    images=image_url,
                    is_liked=is_liked,
                    is_deleted=product.is_deleted,
                    created_at=product.created_at,
                )
                products_data.append(product_data)

            return MyProductsSchemaResponseSchema(
                success=True,
                message="주변 매물 조회가 완료되었습니다.",
                total_count=len(products_data),
                products=products_data,
            )

        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"주변 매물 조회 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )

    @staticmethod
    # 매물 삭제
    def delete_product(user: User, product_id: int):
        if not user.is_authenticated:
            return Response(
                {"success": False, "message": "로그인이 필요합니다."}, status=401
            )

        try:
            with transaction.atomic():  # 트랜잭션 시작
                product = ProductDetail.objects.get(id=product_id)

                # 이미 삭제된 매물인지 확인
                if product.is_deleted:
                    return Response(
                        {"success": False, "message": "이미 삭제된 매물입니다."},
                        status=400,
                    )

                # 삭제 권한 확인
                if product.user != user:
                    return Response(
                        {
                            "success": False,
                            "message": "해당 매물을 삭제할 권한이 없습니다.",
                        },
                        status=403,
                    )

                # 연관된 모든 데이터 soft delete 처리
                # 1. 주소 정보 삭제
                product.address.is_deleted = True
                product.address.save()

                # 2. 이미지 정보 삭제
                ProductImg.objects.filter(product_detail=product).update(
                    is_deleted=True
                )

                # 3. 비디오 정보 삭제
                if product.video:
                    product.video.is_deleted = True
                    product.video.save()

                # 4. 찜하기 정보 삭제
                ProductLikes.objects.filter(product=product).update(is_deleted=True)

                # 5. 매물 정보 삭제
                product.is_deleted = True
                product.save()

                return ProductDeleteResponseSchema(
                    success=True,
                    message="매물이 성공적으로 삭제되었습니다.",
                )

        except ProductDetail.DoesNotExist:
            return Response(
                {"success": False, "message": "매물을 찾을 수 없습니다."}, status=404
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": f"매물 삭제 중 오류가 발생했습니다: {str(e)}",
                },
                status=500,
            )
