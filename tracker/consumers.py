import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from .models import Project


class ProjectConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]
        self.project_group_name = f"project_{self.project_id}"

        # Check if user has access to this project
        if await self.has_project_access():
            await self.channel_layer.group_add(
                self.project_group_name, self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.project_group_name, self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "typing":
                # Handle typing indicator
                await self.channel_layer.group_send(
                    self.project_group_name,
                    {
                        "type": "typing_indicator",
                        "user": self.scope["user"].username,
                        "bug_id": data.get("bug_id"),
                        "is_typing": data.get("is_typing", False),
                    },
                )
        except json.JSONDecodeError:
            pass

    # Handlers for different message types
    async def bug_update(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "bug_update",
                    "event_type": event["event_type"],
                    "bug_id": event["bug_id"],
                    "data": event["data"],
                }
            )
        )

    async def comment_added(self, event):
        await self.send(
            text_data=json.dumps(
                {
                    "type": "comment_added",
                    "bug_id": event["bug_id"],
                    "data": event["data"],
                }
            )
        )

    async def typing_indicator(self, event):
        # Don't send typing indicator back to the sender
        if event["user"] != self.scope["user"].username:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "typing_indicator",
                        "user": event["user"],
                        "bug_id": event["bug_id"],
                        "is_typing": event["is_typing"],
                    }
                )
            )

    async def activity_update(self, event):
        await self.send(
            text_data=json.dumps({"type": "activity_update", "data": event["data"]})
        )

    @database_sync_to_async
    def has_project_access(self):
        try:
            user = self.scope["user"]
            if user.is_anonymous:
                return False

            project = Project.objects.get(id=self.project_id)
            return project.owner == user or user in project.members.all()
        except Project.DoesNotExist:
            return False
