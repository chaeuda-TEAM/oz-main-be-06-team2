from a_apis.auth.bearer import AuthBearer
from a_apis.models.chat import ChatMessage, ChatRoom
from a_apis.models.products import ProductDetail
from a_user.models import User
from ninja import Router
from ninja.responses import Response

router = Router(auth=AuthBearer())


@router.post("/chat/create/")
def create_chat_room(request, item_id: int, buyer_id: int):
    """
    채팅방 생성
    item_id: 게시물 id
    buyer_id: 구매자 id
    """
    try:
        item = ProductDetail.objects.get(id=item_id)
    except ProductDetail.DoesNotExist:
        return Response({"error": "게시물이 없습니다"}, status=404)

    buyer = User.objects.get(id=buyer_id)
    chat_room, created = ChatRoom.objects.get_or_create(
        item=item, seller=item.id, buyer=buyer
    )
    return {"chat_room_id": chat_room.id, "created": created}


@router.get("/chat/{chat_room_id}/messages/")
def get_chat_messages(request, chat_room_id: int):
    messages = ChatMessage.objects.filter(chat_room_id=chat_room_id).order_by(
        "created_at"
    )
    return [
        {
            "sender": msg.sender.username,
            "message": msg.message,
            "sent_at": msg.created_at,
        }
        for msg in messages
    ]


@router.post("/chat/{chat_room_id}/send/")
def send_message(request, chat_room_id: int, sender_id: int, message: str):
    chat_room = ChatRoom.objects.get(id=chat_room_id)
    sender = User.objects.get(id=sender_id)
    msg = ChatMessage.objects.create(
        chat_room=chat_room, sender=sender, message=message
    )
    return {"message_id": msg.id, "sent_at": msg.created_at}
