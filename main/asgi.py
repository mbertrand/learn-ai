import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")

django_asgi_app = get_asgi_application()

import ai_chatbots.routing  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": AuthMiddlewareStack(URLRouter(ai_chatbots.routing.http_patterns)),
        "websocket": AuthMiddlewareStack(
            URLRouter(ai_chatbots.routing.websocket_patterns)
        ),
    }
)
