from application.config import settings
from application.container import Container
from infrastructure.server.server import Server
from presentation.file import FileRouter

media_service = Server(
    name=settings.NAME,
    routers=[FileRouter.api_router],
    start_callbacks=[],
    stop_callbacks=[Container.redis().close],
).app
