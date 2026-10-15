import asyncio
import os

from rich.console import Console

from client.llm_service import chat_with_llm
from client.mcp_service import MCPService

console = Console()


def format_error(error: Exception) -> str:
    exceptions = getattr(error, "exceptions", None)
    if exceptions:
        return "; ".join(format_error(exception) for exception in exceptions)
    return f"{type(error).__name__}: {error}"


async def main() -> None:
    from dotenv import load_dotenv

    load_dotenv()
    token = os.getenv("TASK_MANAGER_TOKEN")
    if not token:
        console.print("[bold red]TASK_MANAGER_TOKEN nije postavljen.[/bold red]")
        return

    server_url = os.getenv("TASK_MANAGER_SERVER_URL", "http://localhost:8000/sse")
    model = os.getenv("OPENAI_MODEL", "")
    try:
        async with MCPService(server_url, token) as service:
            console.print(
                "[bold green]Povezano na MCP Task Manager Server![/bold green]"
            )
            await run_menu(service, model)
    except Exception as error:
        console.print(
            "[bold red]Greška pri spajanju ili komunikaciji sa serverom "
            f"(provjerite da li je pokrenut i da li je token ispravan): "
            f"{error}[/bold red]"
        )


async def run_menu(service: MCPService, model: str) -> None:
    while True:
        console.print("\n[bold cyan]=== MCP Task Manager ===[/bold cyan]")
        console.print("1. Prikaži zadatke (list_tasks)")
        console.print("2. Kreiraj zadatak (create_task)")
        console.print("3. Pročitaj vodič (Resource)")
        console.print("4. Generiši plan za dan (Prompt)")
        console.print("5. Pričaj sa LLM-om (LLM Tool Calling)")
        console.print("0. Izlaz")
        choice = input("Odaberite opciju: ").strip()

        if choice == "1":
            console.print(await service.list_tasks())
        elif choice == "2":
            result = await service.create_task(
                input("Naslov: ").strip(),
                input("Opis: ").strip(),
                input("Korisnik ID: ").strip(),
            )
            console.print(f"[green]{result}[/green]")
        elif choice == "3":
            console.print(f"[yellow]{await service.read_guide()}[/yellow]")
        elif choice == "4":
            console.print(f"[magenta]{await service.get_day_plan()}[/magenta]")
        elif choice == "5":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                console.print("[red]OPENAI_API_KEY nije postavljen u okruženju.[/red]")
                continue
            if not model:
                console.print(
                    "[red]OPENAI_MODEL nije postavljen. Unesite model koji je "
                    "dostupan na izabranom API servisu.[/red]"
                )
                continue
            user_prompt = input(
                "Unesite komandu za LLM "
                "(npr. 'Prikaži moje otvorene zadatke'): "
            )
            try:
                await chat_with_llm(service, user_prompt, api_key, model)
            except Exception as error:
                console.print(
                    f"[bold red]LLM poziv nije uspio: "
                    f"{format_error(error)}[/bold red]"
                )
                console.print(
                    "[yellow]CLI je i dalje aktivan. Provjerite API ključ, "
                    "model i API adresu u .env pa pokušajte ponovo.[/yellow]"
                )
        elif choice == "0":
            break
        else:
            console.print("[red]Nepoznata opcija.[/red]")


if __name__ == "__main__":
    asyncio.run(main())
