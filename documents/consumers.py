import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Document


class DocConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.doc_id = self.scope["url_route"]["kwargs"]["doc_id"]
        self.group = f"doc_{self.doc_id}"
        self.room_users = {}  # channel_name -> username

        # Проверяем, существует ли документ
        self.doc = await self.get_doc(self.doc_id)
        if self.doc is None:
            await self.close()
            return

        # Добавляем в группу и принимаем соединение
        await self.channel_layer.group_add(self.group, self.channel_name)
        await self.accept()

        # Отправляем клиенту текущее состояние документа
        await self.send(json.dumps({
            "type": "init",
            "content": self.doc.content,
            "users": list(self.room_users.values()),
        }))
        await self.broadcast_users()

    async def disconnect(self, code):
        if hasattr(self, "group"):
            self.room_users.pop(self.channel_name, None)
            await self.broadcast_users()
            await self.channel_layer.group_discard(self.group, self.channel_name)
            await self.save_content()

    # ---------- обработка входящих сообщений ----------
    async def receive(self, text_data):
        data = json.loads(text_data)
        kind = data.get("type")

        if kind == "join":
            self.room_users[self.channel_name] = data.get("username", "anon")
            await self.broadcast_users()

        elif kind == "edit":
            # LWW: последнее присланное содержимое побеждает
            await self.channel_layer.group_send(self.group, {
                "type": "doc_edit",
                "content": data["content"],
                "sender": self.channel_name,
            })

        elif kind == "cursor":
            await self.channel_layer.group_send(self.group, {
                "type": "cursor_move",
                "sender": self.channel_name,
                "username": self.room_users.get(self.channel_name, "anon"),
                "pos": data.get("pos", 0),
            })

        elif kind == "chat":
            await self.channel_layer.group_send(self.group, {
                "type": "chat_message",
                "username": self.room_users.get(self.channel_name, "anon"),
                "text": data.get("text", ""),
            })

        elif kind == "save":
            await self.save_content(data.get("content", ""))

    # ---------- рассылка от группы ----------
    async def doc_edit(self, event):
        await self.send(json.dumps({
            "type": "edit",
            "content": event["content"],
            "from_self": event["sender"] == self.channel_name,
        }))

    async def cursor_move(self, event):
        if event["sender"] == self.channel_name:
            return
        await self.send(json.dumps({
            "type": "cursor",
            "username": event["username"],
            "pos": event["pos"],
        }))

    async def chat_message(self, event):
        await self.send(json.dumps({
            "type": "chat",
            "username": event["username"],
            "text": event["text"],
        }))

    async def broadcast_users(self):
        await self.channel_layer.group_send(self.group, {
            "type": "user_list",
            "users": list(self.room_users.values()),
        })

    async def user_list(self, event):
        await self.send(json.dumps({"type": "users", "users": event["users"]}))

    # ---------- работа с БД ----------
    @database_sync_to_async
    def get_doc(self, doc_id):
        return Document.objects.filter(id=doc_id).first()

    async def save_content(self, content=None):
        if content is None:
            content = getattr(self, "_last_content", None)
            if content is None:
                return
        self._last_content = content
        await self._save(self.doc_id, content)

    @database_sync_to_async
    def _save(self, doc_id, content):
        Document.objects.filter(id=doc_id).update(content=content)