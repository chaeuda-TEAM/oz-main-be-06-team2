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
