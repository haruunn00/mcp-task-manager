# MCP Task Manager

Jednostavan task manager koji koristi Model Context Protocol (MCP), SQLite i Python. MCP server nudi alate, resurs i prompt, a CLI klijent komunicira sa serverom preko HTTP/SSE veze. OpenAI integracija je opcionalna.

## MCP koncepti

- **Tool (alat):** izvršna operacija koju klijent ili model može pozvati uz ulazne parametre. Alati ovog servera čitaju i mijenjaju zadatke: `list_tasks`, `get_task`, `create_task`, `update_task_status` i `delete_task`.
- **Resource (resurs):** podaci koje klijent može pročitati kao kontekst; sam resurs ne izvršava komandu niti mijenja stanje. `taskmanager://guide` objašnjava korištenje aplikacije i značenje statusa.
- **Prompt (predložak):** unaprijed definisana poruka koja pomaže modelu da započne određeni zadatak. `plan_my_day` uključuje trenutno aktivne zadatke i traži od modela da napravi dnevni plan, dajući prednost zadacima `in_progress`.


## Struktura projekta

```text
mcp-task-manager/
├── server/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── tools.py
│   ├── resources.py
│   └── prompts.py
├── client/
│   ├── __init__.py
│   ├── cli.py
│   ├── mcp_service.py
│   └── llm_service.py
├── data/
│   └── tasks.db          # kreira se automatski
├── .env.example
├── .env                  # lokalna konfiguracija, nije verzionisana
├── requirements.txt
├── README.md
└── .gitignore
```

Baza `data/tasks.db` se kreira automatski pri prvom pokretanju i nije dio repozitorija. `.env.example` sadrži primjer konfiguracije; kopirajte ga u `.env` i promijenite token prije pokretanja.

## Instalacija

Koristite Python 3.10 ili noviji. Preporučeno je koristiti virtuelno okruženje:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

## Pokretanje

U `.env` postavite vlastiti `TASK_MANAGER_TOKEN`, zatim u prvom terminalu pokrenite server:

```powershell
python -m server.main
```

U drugom terminalu pokrenite klijenta:

```powershell
python -m client.cli
```

Server sluša na `http://localhost:8000`. `TASK_MANAGER_HOST` i `TASK_MANAGER_PORT` mijenjaju adresu servera; postavite odgovarajući `TASK_MANAGER_SERVER_URL` za klijenta. Oba `/sse` i `/messages` endpointa zahtijevaju autentifikaciju preko tokena iz `TASK_MANAGER_TOKEN`.

## CLI opcije

1. Prikaži zadatke
2. Kreiraj zadatak
3. Pročitaj vodič
4. Generiši plan za dan
5. Pošalji zahtjev LLM-u i omogući mu MCP alate
0. Izlaz

MCP server se može povezati i sa drugim MCP klijentima. Za nezavisnu provjeru servera koristite MCP klijentsku aplikaciju/alatu koji podržava SSE; postavite URL `http://localhost:8000/sse` i pošaljite `Authorization: Bearer <TASK_MANAGER_TOKEN>` zaglavlje.

Opcije 1–4 rade bez API ključa. Za opciju 5 postavite `OPENAI_API_KEY`, `OPENAI_BASE_URL` i `OPENAI_MODEL` u `.env`. Za Groq koristite adresu `https://api.groq.com/openai/v1` i model koji je trenutno dostupan na vašem Groq nalogu. OpenAI klijent je kompatibilan s ovim API formatom, ali OpenAI nazivi modela (npr. `gpt-4o-mini`) ne rade automatski na Groq-u.

## Napomene

- Statusi zadataka su `todo`, `in_progress` i `done`.
- MCP server koristi `TASK_MANAGER_TOKEN`; aplikacija neće prihvatiti zahtjev bez postavljenog tokena.
- Ne stavljajte stvarne tokene ili API ključeve u izvorni kod ili repozitorij.
