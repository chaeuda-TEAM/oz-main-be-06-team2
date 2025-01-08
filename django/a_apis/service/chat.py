from a_apis.models.chat import ChatRoom
from a_apis.models.products import ProductDetail
from a_apis.schema.chat import ChatRoomResponse, CreateChatRoomRequest
from ninja.responses import Response
from rest_framework_simplejwt.tokens import AccessToken

from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class ChatService:
    @staticmethod
    def get_chat_rooms(request) -> Response:
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
            chat_rooms = ChatRoom.objects.filter(Q(item__user=user) | Q(buyer=user))
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
                    "success": True,
                    "message": "채팅방 목록을 조회했습니다.",
                    "chat_rooms": [
                        {
                            "id": room.id,
                            "product_id": room.item.id,
                            "product_title": room.item.pro_title,
                            "product_price": room.item.pro_price,
                            "product_address": room.item.address.add_new,
                            "seller": room.item.user.username,
                            "buyer": room.buyer.username,
                        }
                        for room in chat_rooms
                    ],
                },
            )
        except Exception as e:
            print(e)
            return Response(
                status=500,
                data={"success": False, "message": str(e)},
            )

    @staticmethod
    def create_chat_room(request, data: CreateChatRoomRequest) -> Response:
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

            product = ProductDetail.objects.filter(id=data.product_id).first()
            if not product:
                return Response(
                    status=400,
                    data={
                        "success": False,
                        "message": "해당 상품을 찾을 수 없습니다.",
                    },
                )

            # 판매자와 구매자가 같은 경우 채팅방 생성 불가
            if product.user == user:
                return Response(
                    status=400,
                    data={
                        "success": False,
                        "message": "자신의 매물에는 채팅방을 생성할 수 없습니다.",
                    },
                )

            # 이미 존재하는 채팅방인지 확인
            chat_room = ChatRoom.objects.filter(item=product, buyer=user).first()
            if chat_room:
                return Response(
                    status=400,
                    data={
                        "success": False,
                        "message": "이미 존재하는 채팅방입니다.",
                    },
                )

            # 채팅방 생성
            chat_room = ChatRoom.objects.create(
                item=product,
                buyer=user,
            )

            return Response(
                status=200,
                data={
                    "success": True,
                    "message": "채팅방이 생성되었습니다.",
                    "chat_room": {
                        "id": chat_room.id,
                        "product_id": chat_room.item.id,
                        "product_title": chat_room.item.pro_title,
                        "product_price": chat_room.item.pro_price,
                        "product_address": chat_room.item.address.add_new,
                        "seller": chat_room.item.user.username,
                        "buyer": chat_room.buyer.username,
                    },
                },
            )
        except Exception as e:
            return Response(
                status=500,
                data={"success": False, "message": str(e)},
            )
