import json
from logging import getLogger
from pprint import pprint

import asyncpg
from a_core.db import execute_query, init_db
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

from django.conf import settings

logger = getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            await init_db()
            self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
            self.room_group_name = f"chat_{self.room_id}"

            # 채널 레이어 연결 상태 확인
            if not self.channel_layer:
                logger.error("Channel layer is not available")
                await self.close()
                return

            # 채널 레이어에 그룹 추가
            try:
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )
            except Exception as e:
                logger.error(f"Group add error: {str(e)}")
                await self.close()
                return

            await self.accept()
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "connection_established",
                        "message": "Connected to chat room",
                    }
                )
            )

        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            # 그룹에서 채널 제거
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except Exception as e:
            logger.error(f"Disconnection error: {str(e)}")
        finally:
            raise StopConsumer()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data.get("message")
            sender = data.get("sender")

            if not message or not sender:
                raise ValueError("Message and sender are required")

            # SQL 인젝션 방지를 위해 execute_query 사용
            await execute_query(
                """
                INSERT INTO chat_message (sender_id, chat_room_id, message, created_at, updated_at)
                VALUES ($1, $2, $3, NOW(), NOW())
            """,
                int(sender),
                int(self.room_id),
                message,
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat_message", "message": message, "sender": sender},
            )
        except json.JSONDecodeError:
            logger.error("Invalid JSON format")
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Invalid message format"}
                )
            )
        except ValueError as e:
            logger.error(f"Validation error: {e}")
            await self.send(text_data=json.dumps({"type": "error", "message": str(e)}))
        except Exception as e:
            logger.error(f"Message processing error: {e}")
            await self.send(
                text_data=json.dumps(
                    {"type": "error", "message": "Failed to process message"}
                )
            )

    async def chat_message(self, event):
        try:
            await self.send(
                text_data=json.dumps(
                    {"message": event["message"], "sender": event["sender"]}
                )
            )
        except Exception as e:
            print(f"Message send error: {str(e)}")
