from a_apis.auth.bearer import AuthBearer
from a_apis.models.chat import ChatMessage, ChatRoom
from a_apis.models.products import ProductDetail
from a_user.models import User
from ninja import Router
from ninja.responses import Response
from rest_framework_simplejwt.tokens import AccessToken

from django.db.models import Q

router = Router(auth=AuthBearer())


@router.get("/chat")
def get_chat_rooms(request):
    """
    유저가 접속해있는 채팅방 리스트
    """
    try:
        user = request.auth
        if not user:
            return Response(
                status=400,
                data={
                    "success": False,
                    "message": "인증되지 않은 사용자입니다.",
                },
            )

        access_token = AccessToken(user)
        user_id = access_token["user_id"]
        user = User.objects.get(id=user_id)
        chat_rooms = ChatRoom.objects.filter(Q(seller=user) | Q(buyer=user))
        if not chat_rooms:
            return Response(
                status=400,
                data={
                    "success": False,
                    "message": "채팅방이 없습니다.",
                },
            )
        return Response(
            status=200,
            data={
                "chat_rooms": [
                    {
                        "id": room.id,
                        "product_id": room.item.id,
                        "product_title": room.item.pro_title,
                        "seller": room.seller.username,
                        "buyer": room.buyer.username,
                    }
                    for room in chat_rooms
                ],
            },
        )
    except Exception as e:
        return Response(
            status=500,
            data={"success": False, "message": str(e)},
        )
