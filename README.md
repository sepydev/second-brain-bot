# second-brain-bot

A Telegram bot that turns a Markdown knowledge vault into a research
assistant. Add a topic, ask the bot to research it (local knowledge base +
web), review the synthesis as a conversation, then approve it to save a new
note into your vault.

## Architecture

```
Telegram
    |
    v
/research <id>
    |
    v
enqueue Celery task  --------->  Redis (broker/result backend)
                                       |
                                       v
                                Celery worker
                                  - KnowledgeSearch (Markdown vault)
                                  - WebSearch (DuckDuckGo + page fetch)
                                  - Ollama (qwen3.5:9b)
                                       |
                                       v
                                  ResearchResult
                                       |
                                       v
                                    SQLite
                                       |
                                       v
                              Telegram notification
```

- `bot/` — Telegram commands (dynamically discovered from `bot/commands/`)
  and the free-text message handler.
- `database/` — SQLite connection + `ResearchRepository`.
- `knowledge/` — keyword search over the Markdown vault, and the writer
  that saves approved research back into it.
- `web/` — web search + page extraction (`WebSource`).
- `llm/` — LLM abstraction, with an Ollama implementation.
- `research/` — orchestrates knowledge + web + LLM into a `ResearchResult`.
- `tasks/` — the Celery app and the background research/follow-up tasks.

The Telegram bot process only ever enqueues Celery tasks — it never calls
Ollama, the web, or the knowledge search directly, so it stays responsive
while research runs in the background.

## Required local services

Everything runs directly on your Mac, no Docker required.

1. **Redis** — Celery broker/result backend.
   ```
   brew install redis
   brew services start redis
   ```
2. **Ollama** — local LLM runtime.
   ```
   brew install ollama
   ollama serve
   ollama pull qwen3.5:9b
   ```
3. **Telegram bot process** — handles commands and enqueues research jobs.
4. **Celery worker process** — runs research + follow-up tasks in the
   background.

## Configuration

Copy `.env.example` (or create `.env`) with:

```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3.5:9b
SECOND_BRAIN_PATH=/path/to/your/markdown/vault
DATABASE_PATH=data/research.db
REDIS_URL=redis://localhost:6379/0
```

## Setup

```
uv sync
```

## Running

Start Redis and Ollama (see above), then in two separate terminals:

```
# Terminal 1: Telegram bot
uv run second-brain-bot

# Terminal 2: Celery worker
uv run celery -A second_brain_bot.tasks.celery_app worker --loglevel=INFO
```

## Usage

```
/add "CQRS architecture" --category architecture
/list
/research <item_id>
```

`/research` enqueues a background job that searches your knowledge base and
the web, synthesises the findings with qwen3.5:9b, stores the result, and
messages you back when it's ready.

Once a research session is active in a chat, plain text messages are treated
as follow-up questions in that conversation (e.g. "Give me a Django
example.") — these also run through the Celery worker so the bot stays
responsive.

```
/approve
```

Writes the current research result to a new Markdown note under
`SECOND_BRAIN_PATH` (in the item's first category folder, or the vault root
if none) and marks the item `approved`.

## Tests and checks

```
uv run pytest
uv run ruff check
uv run pyright
```
