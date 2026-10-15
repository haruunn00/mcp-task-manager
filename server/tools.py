import json
from typing import Any

from mcp.server import Server
from mcp.types import TextContent, Tool

from server import database


def register_tools(mcp: Server) -> None:
    @mcp.list_tools()
    async def handle_list_tools() -> list[Tool]:
        return [
            Tool(
                name="list_tasks",
                description="Pregled zadataka, uz opcionalno filtriranje po statusu.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": ["string", "null"],
                            "description": (
                                "Opcionalni filter statusa. Koristi jednu od "
                                "dozvoljenih vrijednosti; null ili izostavljen "
                                "status vraća sve zadatke."
                            ),
                            "enum": [*database.TASK_STATUSES, None],
                        }
                    },
                },
            ),
            Tool(
                name="get_task",
                description="Dohvata detalje zadatka na osnovu ID-a.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "Jedinstveni ID zadatka.",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
            Tool(
                name="create_task",
                description="Kreira novi zadatak.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "Kratak naziv zadatka.",
                        },
                        "description": {
                            "type": "string",
                            "description": "Detaljniji opis zadatka.",
                        },
                        "user_id": {
                            "type": "string",
                            "description": "ID korisnika kojem zadatak pripada.",
                        },
                    },
                    "required": ["title", "description", "user_id"],
                },
            ),
            Tool(
                name="update_task_status",
                description="Mijenja status zadatka.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "Jedinstveni ID zadatka za ažuriranje.",
                        },
                        "status": {
                            "type": "string",
                            "description": "Novi status zadatka.",
                            "enum": list(database.TASK_STATUSES),
                        },
                    },
                    "required": ["task_id", "status"],
                },
            ),
            Tool(
                name="delete_task",
                description="Briše zadatak na osnovu ID-a.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "integer",
                            "description": "Jedinstveni ID zadatka za brisanje.",
                        }
                    },
                    "required": ["task_id"],
                },
            ),
        ]

    @mcp.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any]
    ) -> list[TextContent]:
        if name == "list_tasks":
            tasks = database.list_tasks(arguments.get("status"))
            return [
                TextContent(type="text", text=json.dumps(tasks, ensure_ascii=False))
            ]

        if name == "get_task":
            task = database.get_task(arguments["task_id"])
            if task is None:
                return [TextContent(type="text", text="Zadatak nije pronađen.")]
            return [
                TextContent(
                    type="text", text=json.dumps(task, ensure_ascii=False)
                )
            ]

        if name == "create_task":
            database.create_task(
                arguments["title"],
                arguments["description"],
                arguments["user_id"],
            )
            return [TextContent(type="text", text="Zadatak uspješno kreiran.")]

        if name == "update_task_status":
            status = arguments["status"]
            if not database.update_task_status(arguments["task_id"], status):
                return [TextContent(type="text", text="Zadatak nije pronađen.")]
            return [
                TextContent(
                    type="text",
                    text=f"Status zadatka {arguments['task_id']} ažuriran u {status}.",
                )
            ]

        if name == "delete_task":
            if not database.delete_task(arguments["task_id"]):
                return [TextContent(type="text", text="Zadatak nije pronađen.")]
            return [TextContent(type="text", text="Zadatak izbrisan.")]

        raise ValueError(f"Nepoznat alat: {name}")
