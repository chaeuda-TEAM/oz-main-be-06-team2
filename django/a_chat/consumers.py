import json
from pprint import pprint

import asyncpg
from channels.exceptions import StopConsumer
from channels.generic.websocket import AsyncWebsocketConsumer

from django.conf import settings


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
            self.room_group_name = f"chat_{self.room_id}"

            # 채널 레이어 연결 상태 확인
            if not self.channel_layer:
                print("Channel layer is not available")
                await self.close()
                return

            # 채널 레이어에 그룹 추가
            try:
                await self.channel_layer.group_add(
                    self.room_group_name, self.channel_name
                )
            except Exception as e:
                print(f"Group add error: {str(e)}")
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
            print(f"Connection error: {str(e)}")
            await self.close()

    async def postgresql_db_connect(self):
        try:
            self.db_pool = await asyncpg.create_pool(
                user=settings.DATABASES["default"]["USER"],
                password=settings.DATABASES["default"]["PASSWORD"],
                database=settings.DATABASES["default"]["NAME"],
                host=settings.DATABASES["default"]["HOST"],
                port=settings.DATABASES["default"]["PORT"],
            )
        except Exception as e:
            print(f"Database connection error: {str(e)}")

    async def disconnect(self, close_code):
        try:
            # 그룹에서 채널 제거
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )
        except Exception as e:
            print(f"Disconnection error: {str(e)}")
        finally:
            raise StopConsumer()

    async def receive(self, text_data):
        try:
            print(f"{text_data = }")
            print(json.dumps(self.__dict__, indent=4, default=str))
            data = json.loads(text_data)
            message = data["message"]
            sender = data["sender"]

            # 그룹으로 메시지 전송
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "chat_message", "message": message, "sender": sender},
            )
        except Exception as e:
            print(f"Message receive error: {str(e)}")
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
