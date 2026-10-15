from mcp.server import Server
from mcp.types import GetPromptResult, Prompt, PromptMessage, TextContent

from server import database


def register_prompts(mcp: Server) -> None:
    @mcp.list_prompts()
    async def handle_list_prompts() -> list[Prompt]:
        return [
            Prompt(
                name="plan_my_day",
                description="Predlaže plan za dan na osnovu aktivnih zadataka.",
                arguments=[],
            )
        ]

    @mcp.get_prompt()
    async def handle_get_prompt(
        name: str, arguments: dict[str, str] | None
    ) -> GetPromptResult:
        if name != "plan_my_day":
            raise ValueError(f"Prompt nije pronađen: {name}")

        tasks = database.run_query(
            "SELECT * FROM tasks WHERE status != 'done' ORDER BY id"
        )
        task_list = "\n".join(
            f"- {task['title']} ({task['status']})" for task in tasks
        ) or "- Nema aktivnih zadataka."
        return GetPromptResult(
            description="Plan dana zasnovan na aktivnim zadacima.",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=(
                            f"Evo mojih aktivnih zadataka:\n{task_list}\n\n"
                            "Napravi optimalan plan za današnji dan i prvo završi "
                            "zadatke koji su već u statusu 'in_progress'."
                        ),
                    ),
                )
            ],
        )
