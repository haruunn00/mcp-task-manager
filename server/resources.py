from mcp.server import Server
from mcp.types import Resource


def register_resources(mcp: Server) -> None:
    @mcp.list_resources()
    async def handle_list_resources() -> list[Resource]:
        return [
            Resource(
                uri="taskmanager://guide",
                name="Upute za Task Manager",
                mimeType="text/plain",
            )
        ]

    @mcp.read_resource()
    async def handle_read_resource(uri: str) -> str:
        if str(uri) == "taskmanager://guide":
            return (
                "Vodič:\n"
                "Statusi: 'todo' (za uraditi), 'in_progress' (radi se), "
                "'done' (završeno). Prioritet dajte zadacima u statusu "
                "'in_progress'."
            )
        raise ValueError(f"Resurs nije pronađen: {uri}")
