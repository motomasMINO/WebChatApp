import json
from channels.generic.websocket import AsyncWebsocketConsumer

# WebSocketを通じてリアルタイムでチャットメッセージをやり取りするためのコンシューマー
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # 全員同じ "chat" ルームに入れる
        self.room_group_name = "chat"

        # グループに追加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    # WebSocketが切断されたときの処理
    async def disconnect(self, close_code):
        # グループから削除
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # クライアントからメッセージを受信
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = self.scope["user"].username if self.scope["user"].is_authenticated else "Anonymous"

        # グループにブロードキャスト
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": user,
            }
        )

    # グループから送られてきたメッセージを WebSocket に送信
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "user": event["user"],
        }))