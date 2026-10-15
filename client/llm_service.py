import json
import os
from typing import Any

from openai import AsyncOpenAI
from rich.console import Console

from client.mcp_service import MCPService

console = Console()


async def chat_with_llm(
    service: MCPService, user_prompt: str, api_key: str, model: str
) -> None:
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=os.getenv(
            "OPENAI_BASE_URL", "https://api.groq.com/openai/v1"
        ),
    )
    mcp_tools = await service.list_tools()
    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            },
        }
        for tool in mcp_tools
    ]
    messages: list[Any] = [{"role": "user", "content": user_prompt}]

    for _ in range(5):
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=openai_tools,
        )
        response_message = response.choices[0].message
        if not response_message.tool_calls:
            console.print(
                f"\n[bold blue]LLM odgovor:[/bold blue] "
                f"{response_message.content or ''}"
            )
            return

        messages.append(response_message.model_dump(exclude_none=True))
        for tool_call in response_message.tool_calls:
            tool_name = tool_call.function.name
            tool_arguments = json.loads(tool_call.function.arguments)
            console.print(
                f"[italic]LLM poziva alat: {tool_name}({tool_arguments})[/italic]"
            )
            tool_result = await service.call_tool(tool_name, tool_arguments)
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": tool_result,
                }
            )

    console.print(
        "[yellow]LLM je dostigao ograničenje od 5 uzastopnih poziva alata.[/yellow]"
    )
