from typing import Optional

from ninja import Schema


class AddressSchema(Schema):
    add_new: str
    add_old: str
    latitude: float
    longitude: float


class AddressDataSchema(Schema):
    user: str
    add_new: str
    add_old: str
    latitude: float
    longitude: float


class AddressResponseSchema(Schema):
    success: bool
    message: str
    data: Optional[AddressDataSchema] = None


class ProductSchema(Schema):
    pro_title: str
    pro_price: int
    pro_supply_a: float
    pro_site_a: float
    pro_heat: str
    pro_type: str
    pro_floor: str
    pro_intro: str
    sale: bool


class Cost(Schema):
    cost_type: str
    mg_cost: int
