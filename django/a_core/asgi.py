import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "a_core.settings.product_asgi")
django.setup()
import a_chat.routing
from a_core.db import close_db, init_db
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

from django.core.asgi import get_asgi_application


async def lifespan(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await init_db()
                await send({"type": "lifespan.startup.complete"})
            elif message["type"] == "lifespan.shutdown":
                await close_db()
                await send({"type": "lifespan.shutdown.complete"})
                return


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(a_chat.routing.websocket_urlpatterns)
        ),
        "lifespan": lifespan,
    }
)
