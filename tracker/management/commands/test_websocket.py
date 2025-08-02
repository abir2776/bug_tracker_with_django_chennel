import asyncio
import json
import os

from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from dotenv import load_dotenv

from bugtracker.asgi import application

load_dotenv()

User = get_user_model()


class Command(BaseCommand):
    help = "Test Project WebSocket connection"

    def add_arguments(self, parser):
        parser.add_argument("project_id", type=int, help="Project ID to test websocket")

    def handle(self, *args, **options):
        project_id = options["project_id"]
        asyncio.run(self.test_websocket(project_id))

    async def test_websocket(self, project_id):
        try:
            user = await self.get_test_user()
            communicator = WebsocketCommunicator(
                application, f"/ws/project/{project_id}/"
            )
            communicator.scope["user"] = user

            connected, _ = await communicator.connect()

            if connected:
                self.stdout.write(
                    self.style.SUCCESS("✅ WebSocket connected successfully")
                )
                await communicator.send_json_to(
                    {"type": "typing", "bug_id": 1, "is_typing": True}
                )
                try:
                    response = await asyncio.wait_for(
                        communicator.receive_json_from(), timeout=2
                    )
                    self.stdout.write(
                        self.style.SUCCESS(f"📩 Received: {json.dumps(response)}")
                    )
                except asyncio.TimeoutError:
                    self.stdout.write(self.style.WARNING("⚠ No response received"))

                try:
                    await communicator.disconnect()
                except asyncio.CancelledError:
                    pass
            else:
                self.stdout.write(self.style.ERROR("❌ Failed to connect to WebSocket"))
        except Exception as e:
            self.stderr.write(f"Error: {e}")

    @staticmethod
    async def get_test_user():
        user, _ = await asyncio.to_thread(
            lambda: User.objects.get_or_create(
                email=os.getenv("WEBSOCKET_TEST_USER_EMAIL"),
                defaults={"password": os.getenv("WEBSOCKET_TEST_USER_PASS")},
            )
        )
        return user
