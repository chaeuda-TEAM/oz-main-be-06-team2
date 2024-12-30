from enum import Enum
from typing import Optional

from ninja import Schema
from ninja.files import UploadedFile


class AddressSchema(Schema):
    add_new: str
    add_old: str
    latitude: float
    longitude: float


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
    pro_title: str
    pro_price: int
    management_cost: int
    pro_supply_a: float
    pro_site_a: float
    pro_heat: HeatType
    pro_type: BuildingType
    pro_floor: int
    description: str
    sale: bool


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
    images: list[str]
    video: Optional[str] = None
    detail: ProductDetailSchema
    address: AddressSchema

