from typing import Optional

from ninja import Schema


class AddressSchema(Schema):
    add_new: str
    add_old: str
    latitude: float
    longitude: float
