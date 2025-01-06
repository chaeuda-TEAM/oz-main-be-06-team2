from a_apis.models.products import ProductDetail
from a_common.models import CommonModel
from a_user.models import User

from django.db import models


class ChatRoom(CommonModel):
    """1:1 채팅방"""

    item = models.ForeignKey(
        ProductDetail, related_name="chat_rooms", on_delete=models.CASCADE
    )
    seller = models.ForeignKey(
        User, related_name="chat_rooms_as_seller", on_delete=models.CASCADE
    )
    buyer = models.ForeignKey(
        User, related_name="chat_rooms_as_buyer", on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "chat_room"
        verbose_name = "채팅방"
        verbose_name_plural = "채팅방"
        unique_together = ("item", "seller", "buyer")

    def __str__(self):
        return f"ChatRoom for {self.item.pro_title} ({self.seller.username} ↔ {self.buyer.username})"


class ChatMessage(CommonModel):
    """채팅 메시지"""

    chat_room = models.ForeignKey(
        ChatRoom, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    message = models.TextField()

    class Meta:
        db_table = "chat_message"
        verbose_name = "채팅 메시지"
        verbose_name_plural = "채팅 메시지"

    def __str__(self):
        return f"{self.sender.username}: {self.message[:20]}"
