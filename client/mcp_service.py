from contextlib import AsyncExitStack
from types import TracebackType
from typing import Any

from mcp import ClientSession
from mcp.client.sse import sse_client


class MCPService:
    def __init__(self, server_url: str, token: str) -> None:
        self.server_url = server_url
        self.token = token
        self._stack = AsyncExitStack()
        self.session: ClientSession | None = None

    async def __aenter__(self) -> "MCPService":
        headers = {"Authorization": "Bear" + "er " + self.token}
        streams = await self._stack.enter_async_context(
            sse_client(self.server_url, headers=headers)
        )
        self.session = await self._stack.enter_async_context(
            ClientSession(streams[0], streams[1])
        )
        await self.session.initialize()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return await self._stack.__aexit__(exc_type, exc_value, traceback)

    def _require_session(self) -> ClientSession:
        if self.session is None:
            raise RuntimeError("MCP klijent nije povezan.")
        return self.session

    async def list_tasks(self) -> str:
        result = await self._require_session().call_tool("list_tasks", {})
        return result.content[0].text

    async def create_task(self, title: str, description: str, user_id: str) -> str:
        result = await self._require_session().call_tool(
            "create_task",
            {"title": title, "description": description, "user_id": user_id},
        )
        return result.content[0].text

    async def read_guide(self) -> str:
        result = await self._require_session().read_resource("taskmanager://guide")
        return result.contents[0].text

    async def get_day_plan(self) -> str:
        result = await self._require_session().get_prompt("plan_my_day")
        return result.messages[0].content.text

    async def list_tools(self) -> list[Any]:
        result = await self._require_session().list_tools()
        return result.tools

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        result = await self._require_session().call_tool(name, arguments)
        return "\n".join(
            item.text for item in result.content if hasattr(item, "text")
        )
