from datetime import datetime
from enum import Enum
from typing import Optional, Union

from ninja import Field, Schema
from ninja.files import UploadedFile


class HeatType(str, Enum):
    GAS = "gas"
    OIL = "oil"
    BRIQUETTE = "briquette"
    HEAT_ETC = "heat_etc"


class BuildingType(str, Enum):
    DETACHED = "detached"
    MULTI = "multi"
    TYPE_ETC = "type_etc"


# 매물 등록/수정 api RequestBody 스키마
class ProductRequestBodySchema(Schema):
    pro_title: str = Field(..., description="제목")
    pro_price: int = Field(..., description="매물금액")
    management_cost: Optional[int] = Field(default=None, description="관리비")
    pro_supply_a: float = Field(..., description="공급면적(평수)")
    pro_site_a: float = Field(..., description="부지면적")
    pro_heat: HeatType = Field(..., description="난방방식")
    pro_type: BuildingType = Field(..., description="건물유형")
    pro_floor: int = Field(..., description="층")
    description: str = Field(..., description="상세설명")
    sale: Optional[bool] = Field(
        default=True, description="판매여부"
    )  # sale을 선택적 필드로 변경하고 기본값을 True로 설정
    pro_rooms: int = Field(..., description="방 갯수")
    pro_bathrooms: int = Field(..., description="욕실 갯수")
    pro_construction_year: int = Field(..., description="건축연도")
    add_new: str = Field(..., description="도로명주소")
    add_old: str = Field(..., description="구주소")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")


# 매물생성 응답데이터 *상세* 스키마
class ProductResponseDetailSchema(Schema):
    product_id: int
    images: list[str]
    video: Optional[str] = None
    pro_title: str = Field(..., description="제목")
    pro_price: int = Field(..., description="매물금액")
    management_cost: Optional[int] = Field(default=None, description="관리비")
    pro_supply_a: float = Field(..., description="공급면적(평수)")
    pro_site_a: float = Field(..., description="부지면적")
    pro_heat: HeatType = Field(..., description="난방방식")
    pro_type: BuildingType = Field(..., description="건물유형")
    pro_floor: int = Field(..., description="층")
    description: str = Field(..., description="상세설명")
    sale: Optional[bool] = Field(default=True, description="판매여부")
    pro_rooms: int = Field(..., description="방 갯수")
    pro_bathrooms: int = Field(..., description="욕실 갯수")
    pro_construction_year: int = Field(..., description="건축연도")
    add_new: str = Field(..., description="도로명주소")
    add_old: str = Field(..., description="구주소")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    is_liked: bool = Field(..., description="현재 사용자의 찜 여부")
    created_at: datetime = Field(..., description="등록일")
    updated_at: datetime = Field(..., description="수정일")


# 매물 등록 api response 스키마
class ProductAllResponseSchema(Schema):
    success: bool
    message: str
    product: ProductResponseDetailSchema


# 매물수정 응답데이터 *상세* 스키마
class ProductUpdateResponseDetailSchema(Schema):
    product_id: int
    images: Optional[list[str]] = None
    video: Optional[str] = None
    pro_title: str = Field(..., description="제목")
    pro_price: int = Field(..., description="매물금액")
    management_cost: Optional[int] = Field(default=None, description="관리비")
    pro_supply_a: float = Field(..., description="공급면적(평수)")
    pro_site_a: float = Field(..., description="부지면적")
    pro_heat: HeatType = Field(..., description="난방방식")
    pro_type: BuildingType = Field(..., description="건물유형")
    pro_floor: int = Field(..., description="층")
    description: str = Field(..., description="상세설명")
    sale: Optional[bool] = Field(default=True, description="판매여부")
    pro_rooms: int = Field(..., description="방 갯수")
    pro_bathrooms: int = Field(..., description="욕실 갯수")
    pro_construction_year: int = Field(..., description="건축연도")
    add_new: str = Field(..., description="도로명주소")
    add_old: str = Field(..., description="구주소")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    is_liked: bool = Field(..., description="현재 사용자의 찜 여부")
    created_at: datetime = Field(..., description="등록일")
    updated_at: datetime = Field(..., description="수정일")


# 매물수정 api response 스키마
class ProductUpdateResponseSchema(Schema):
    success: bool
    message: str
    product: ProductUpdateResponseDetailSchema


# 찜하기 api response 스키마
class ProductLikeResponseSchema(Schema):
    success: bool
    message: str
    is_liked: bool  # 찜하기 상태
    created_at: Optional[datetime] = Field(
        None, description="찜하기 생성 시간"
    )  # None 허용


# 유저가 찜한 매물 목록 조회 스키마
class UserLikedProductsSchema(Schema):
    product_id: int = Field(..., description="매물 ID")
    pro_title: str = Field(..., description="매물 제목")
    pro_price: int = Field(..., description="매물 가격")
    pro_type: str = Field(..., description="건물 유형")
    pro_supply_a: float = Field(..., description="공급면적")
    add_new: str = Field(..., description="매물 주소(도로명)")
    images: Optional[str] = Field(None, description="매물 이미지 URL(첫 번째 이미지)")
    is_liked: bool = Field(..., description="현재 사용자의 찜 여부")
    created_at: datetime = Field(..., description="찜한 시간")


# 유저가 찜한 매물 목록 조회 응답 스키마
class UserLikedProductsResponseSchema(Schema):
    success: bool = Field(..., description="요청 처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    total_count: int = Field(..., description="전체 찜한 매물 수")
    products: list[UserLikedProductsSchema] = Field(..., description="찜한 매물 목록")


# 유저가 등록한 매물 목록 조회 스키마
class MyProductsSchema(Schema):
    product_id: int = Field(..., description="매물 ID")
    pro_title: str = Field(..., description="매물 제목")
    pro_price: int = Field(..., description="매물 가격")
    pro_type: str = Field(..., description="건물 유형")
    pro_supply_a: float = Field(..., description="공급면적")
    add_new: str = Field(..., description="매물 주소(도로명)")
    images: Optional[str] = Field(None, description="매물 이미지 URL(첫 번째 이미지)")
    is_liked: bool = Field(..., description="현재 사용자의 찜 여부")
    created_at: datetime = Field(..., description="찜한 시간")


# 유저가 등록한 매물 목록 조회 응답 스키마
class MyProductsSchemaResponseSchema(Schema):
    success: bool = Field(..., description="요청 처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    total_count: int = Field(..., description="전체 등록 매물 수")
    products: list[MyProductsSchema] = Field(..., description="등록한 매물 목록")


# 매물 상세조회를 위한 유저 정보 스키마
class UserDetailSchema(Schema):
    id: int = Field(..., description="유저 ID")
    username: str = Field(..., description="유저 이름")
    phone_number: str = Field(..., description="유저 휴대폰번호")


# 매물 상세조회 응답 스키마
class ProductInformationResponseSchema(Schema):
    product_id: int = Field(..., description="매물 ID")
    user: UserDetailSchema = Field(..., description="매물 등록 유저 정보")
    images: list[str] = Field(..., description="매물 이미지 URL 목록")
    video: Optional[str] = Field(None, description="매물 동영상 URL")
    pro_title: str = Field(..., description="제목")
    pro_price: int = Field(..., description="매물금액")
    management_cost: Optional[int] = Field(default=None, description="관리비")
    pro_supply_a: float = Field(..., description="공급면적(평수)")
    pro_site_a: float = Field(..., description="부지면적")
    pro_heat: HeatType = Field(..., description="난방방식")
    pro_type: BuildingType = Field(..., description="건물유형")
    pro_floor: int = Field(..., description="층")
    description: str = Field(..., description="상세설명")
    sale: Optional[bool] = Field(default=True, description="판매여부")
    pro_rooms: int = Field(..., description="방 갯수")
    pro_bathrooms: int = Field(..., description="욕실 갯수")
    pro_construction_year: int = Field(..., description="건축연도")
    add_new: str = Field(..., description="도로명주소")
    add_old: str = Field(..., description="구주소")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")
    is_liked: bool = Field(..., description="현재 사용자의 찜 여부")
    created_at: datetime = Field(..., description="등록일")
    updated_at: datetime = Field(..., description="수정일")


# 최종 매물 상세조회 응답 스키마
class ProductDetailAllResponseSchema(Schema):
    success: bool = Field(..., description="요청 처리 성공 여부")
    message: str = Field(..., description="응답 메시지")
    product: ProductInformationResponseSchema = Field(..., description="매물 상세 정보")
