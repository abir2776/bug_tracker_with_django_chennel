import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import tracker.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bugtracker.settings')

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(tracker.routing.websocket_urlpatterns)
        ),
    }
)