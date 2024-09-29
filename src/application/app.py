from application.config import settings
from application.container import Container
from infrastructure.server.server import Server

media_service = Server(
    name=settings.NAME,
    routers=[],
    start_callbacks=[],
    stop_callbacks=[Container.redis().close],
).app
