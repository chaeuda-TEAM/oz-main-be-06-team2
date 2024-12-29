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


class ProductDetailSchema(Schema):
    pro_title: str
    pro_price: int
    pro_supply_a: float
    pro_site_a: float
    pro_heat: str
    pro_type: str
    pro_floor: str
    pro_intro: str
    sale: bool


class CostSchema(Schema):
    cost_type: str
    mg_cost: int


class ImageSchema(Schema):
    img_url: str


class VideoSchema(Schema):
    video_url: str


# 매물등록 api request body 스키마
class ProductAllSchema(Schema):
    detail: ProductDetailSchema
    cost: CostSchema
    address: AddressSchema


# 매물등록 api response 스키마
class ProductAllResponseSchema(Schema):
    success: bool
    message: str
    images: list[str]
    video: Optional[str] = None
    detail: ProductDetailSchema
    cost: CostSchema
    address: AddressSchema
