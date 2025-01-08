from typing import Optional

from ninja import Schema


class CreateChatRoomRequest(Schema):
    product_id: int


class ChatRoom(Schema):
    id: int
    product_id: int
    product_title: str
    product_price: int
    product_address: str
    seller: str
    buyer: str


class ChatRoomResponse(Schema):
    chat_rooms: list[ChatRoom] = []


class GetChatRoomsResponse(Schema):
    success: bool
    message: str
    chat_rooms: Optional[ChatRoomResponse] = None
