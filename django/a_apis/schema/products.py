from enum import Enum
from typing import Optional, Union

from ninja import Field, Schema
from ninja.files import UploadedFile


class AddressSchema(Schema):
    add_new: str = Field(..., description="도로명주소")
    add_old: str = Field(..., description="구주소")
    latitude: float = Field(..., description="위도")
    longitude: float = Field(..., description="경도")


class AddressResponseSchema(Schema):
    success: bool
    message: str
    data: Optional[AddressSchema] = None


class HeatType(str, Enum):
    GAS = "gas"
    OIL = "oil"
    BRIQUETTE = "briquette"
    HEAT_ETC = "heat_etc"


class BuildingType(str, Enum):
    DETACHED = "detached"
    MULTI = "multi"
    TYPE_ETC = "type_etc"


class ProductDetailSchema(Schema):
    pro_title: str = Field(..., description="제목")
    pro_price: int = Field(..., description="매물금액")
    management_cost: Optional[int] = Field(
        default=None, description="관리비"
    )  # sale을 선택적 필드로 변경하고 기본값을 None으로 설정
    pro_supply_a: float = Field(..., description="공급면적(평수)")
    pro_site_a: float = Field(..., description="부지면적")
    pro_heat: HeatType = Field(..., description="난방방식")
    pro_type: BuildingType = Field(..., description="건물유형")
    pro_floor: int = Field(..., description="층")
    description: str = Field(..., description="상세설명")
    sale: Optional[bool] = Field(
        default=True, description="판매여부"
    )  # sale을 선택적 필드로 변경하고 기본값을 True로 설정


class ImageSchema(Schema):
    img_url: str


class VideoSchema(Schema):
    video_url: str


# 매물등록 api request body 스키마
class ProductAllSchema(Schema):
    detail: ProductDetailSchema
    address: AddressSchema


# 매물등록 api response 스키마
class ProductAllResponseSchema(Schema):
    success: bool
    message: str
    product_id: int
    images: list[str]
    video: Optional[str] = None
    detail: ProductDetailSchema
    address: AddressSchema


class ProductUpdateResponseSchema(Schema):
    success: bool
    message: str
    product_id: int
    images: Optional[list[str]] = None
    video: Optional[str] = None
    detail: ProductDetailSchema
    address: AddressSchema
