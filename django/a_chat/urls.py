from django.urls import path

from . import views

urlpatterns = [
    # 채팅 관련 URL 패턴들
    path("", views.chat_home, name="chat_home"),  # 예시: 채팅 홈
    path("<str:room_name>/", views.chat_room, name="chat_room"),  # 예시: 채팅방
]
