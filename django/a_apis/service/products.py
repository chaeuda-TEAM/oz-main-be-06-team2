import os

import requests
from a_apis.models.products import ProductAddress, ProductDetail
from a_apis.schema.products import AddressSchema
from dotenv import load_dotenv
from ninja.errors import HttpError

from django.contrib.auth.models import User
from django.http import JsonResponse

# load_dotenv()

# class MapService:
#     @staticmethod
#     def create_product_address(payload: AddressRequestSchema) -> JsonResponse:
#         address = payload.add_new
#         naver_api_url = "https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode"
#         headers = {
#             "X-NCP-APIGW-API-KEY-ID": os.getenv("NAVER_API_KEY_ID"),
#             "X-NCP-APIGW-API-KEY": os.getenv("NAVER_API_KEY")
#         }
#         params = {"query": address}
#         response = requests.get(naver_api_url, headers=headers, params=params)
#         if response.status_code == 200:
#             data = response.json()
#             if data['addresses']:
#                 location = data['addresses'][0]
#                 product_address = ProductAddress(
#                     add_new=payload.add_new,
#                     add_old=payload.add_old,
#                     latitude=location['y'],
#                     longitude=location['x']
#                 )
#                 product_address.save()
#                 return JsonResponse({'latitude': location['y'], 'longitude': location['x']}, status=201)
#             return JsonResponse({"error": "No location found"}, status=404)
#         return JsonResponse({"error": "Naver API error"}, status=500)


class AddressService:
    @staticmethod
    def save_product_address(user: User, data: AddressSchema) -> dict:
        try:
            # 주소 데이터를 DB에 저장
            address = ProductAddress.objects.create(
                add_new=data.add_new,
                add_old=data.add_old,
                latitude=data.latitude,
                longitude=data.longitude,
            )

            # ProductDetail에 주소 연결
            ProductDetail.objects.create(
                user_no=user,  # 로그인된 유저 정보
                address_id=address,
                # 다른 필드들은 필요에 따라 추가하면 됨
            )

            return {
                "success": True,
                "message": "주소 및 위도경도 저장 완료",
                "data": {
                    "user": user.username,
                    "add_new": data.add_new,
                    "add_old": data.add_old,
                    "latitude": data.latitude,
                    "longitude": data.longitude,
                },
            }
        except Exception as e:
            raise HttpError(500, f"데이터 저장 중 오류가 발생했습니다: {str(e)}")
