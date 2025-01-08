from a_apis.auth.bearer import AuthBearer
from a_apis.schema.chat import (
    ChatRoomResponse,
    CreateChatRoomRequest,
    GetChatRoomsResponse,
)
from a_apis.service.chat import ChatService
from ninja import Router

router = Router(auth=AuthBearer())


@router.get("/list", response=GetChatRoomsResponse)
def get_chat_rooms(request):
    """
    유저가 접속해있는 채팅방 리스트
    """
    return ChatService.get_chat_rooms(request)


@router.post("/create", response=ChatRoomResponse)
def create_chat_room(request, data: CreateChatRoomRequest):
    """
    채팅방 생성
    """
    return ChatService.create_chat_room(request, data)
