import hmac
import os

import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from server.database import init_db
from server.prompts import register_prompts
from server.resources import register_resources
from server.tools import register_tools

init_db()
mcp = Server("TaskManager")
register_tools(mcp)
register_resources(mcp)
register_prompts(mcp)
sse = SseServerTransport("/messages")


def is_authorized(request: Request) -> bool:
    token = os.getenv("TASK_MANAGER_TOKEN")
    if not token:
        raise RuntimeError("Varijabla TASK_MANAGER_TOKEN nije postavljena.")
    supplied = request.headers.get("Authorization", "")
    expected = "Bear" + "er " + token
    return hmac.compare_digest(supplied, expected)


async def sse_handler(request: Request) -> Response:
    if not is_authorized(request):
        return Response("Unauthorized", status_code=401)
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as streams:
        await mcp.run(
            streams[0], streams[1], mcp.create_initialization_options()
        )
    return Response()


async def messages_handler(scope: Scope, receive: Receive, send: Send) -> None:
    request = Request(scope, receive)
    if not is_authorized(request):
        await Response("Unauthorized", status_code=401)(scope, receive, send)
        return
    await sse.handle_post_message(scope, receive, send)


app = Starlette(
    routes=[
        Route("/sse", endpoint=sse_handler),
        Mount("/messages", app=messages_handler),
    ]
)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    if not os.getenv("TASK_MANAGER_TOKEN"):
        raise RuntimeError("Postavite TASK_MANAGER_TOKEN prije pokretanja servera.")
    uvicorn.run(
        app,
        host=os.getenv("TASK_MANAGER_HOST", "127.0.0.1"),
        port=int(os.getenv("TASK_MANAGER_PORT", "8000")),
    )
