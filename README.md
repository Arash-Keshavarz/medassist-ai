<div align="center">
  <img src="assets/medassist-logo.png" alt="MedAssist AI Logo" width="220">

  # MedAssist AI

  Evidence-Grounded Medical Research Assistant
</div>


This Project initially focused on
ECG, PPG, rPPG, physiological monitoring, signal quality, and motion artifacts.
This is a research portfolio project, not a clinical diagnosis or treatment system.

## Current scope

Checkpoint 1 implements the FastAPI foundation, validated configuration, health
endpoint, and a typed LLM provider contract. Research questions, PubMed retrieval,
inference, and citation validation are not implemented yet. No API key is required
and no paid LLM calls are made.

## Setup and run

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and use Python
3.11 or newer. From the repository root:

```powershell
uv sync
# Optional: copy only if you do not already have a local .env file.
Copy-Item .env.example .env
uv run uvicorn medassist.main:app --reload
```

On macOS/Linux, the optional copy command is `cp -n .env.example .env`.
`uv sync` installs the package and development tools into `.venv`, using
[uv.lock](uv.lock). The first sync needs network access unless dependencies are
already cached. Python can also be selected explicitly with `uv sync --python 3.11`.

- Health: <http://127.0.0.1:8000/health>
- Swagger UI: <http://127.0.0.1:8000/docs>
- OpenAPI schema: <http://127.0.0.1:8000/openapi.json>

```json
{"service": "medassist-ai", "version": "0.1.0", "status": "ok"}
```

Health reports application liveness only; it does not verify PubMed or LLM
availability. FastAPI serves the Swagger HTML locally, but its default UI assets
load from a CDN and require browser internet access.

## Configuration

[Settings](src/medassist/core/config.py) uses `pydantic-settings`. Precedence is
explicit constructor values, environment variables, the optional `.env` file in
the current working directory, then defaults. Start from the repository root to
load your local `.env` file. Restart the app after changing configuration.

| Environment variable | Default | Purpose |
| --- | --- | --- |
| `MEDASSIST_SERVICE_NAME` | `medassist-ai` | Health response and API title |
| `MEDASSIST_LLM_PROVIDER` | `openai` | Future provider selection |
| `MEDASSIST_LLM_MODEL` | unset | Future hosted model selection |
| `MEDASSIST_LLM_API_KEY` | unset | Optional `SecretStr` credential |
| `MEDASSIST_LLM_MAX_OUTPUT_TOKENS` | `1024` | Positive output token budget |
| `MEDASSIST_PUBMED_RESULT_LIMIT` | `10` | Result count, from 1 to 100 |
| `MEDASSIST_REQUEST_TIMEOUT_SECONDS` | `30` | Positive, finite HTTP timeout |

Empty environment values are ignored, so the example's blank model and key remain
unset. Provider names are configuration strings; they do not imply an adapter is
already implemented. Invalid values fail startup rather than being silently fixed.
Unrelated dotenv entries are ignored to allow shared local environment files.

Keep credentials in local environment variables or an ignored `.env` file.
`SecretStr` masks normal representations and JSON serialization; it is not
encryption. Do not log credentials or whole settings objects. No model name is
hardcoded, and future inference must validate model/provider/credentials before use.

## Architecture

- [application.py](src/medassist/application.py): importable application factory.
- [main.py](src/medassist/main.py): Uvicorn entry point that loads configuration.
- [api/](src/medassist/api/): HTTP routing and dependency resolution.
- [core/](src/medassist/core/): environment configuration and validation.
- [schemas/](src/medassist/schemas/): typed public response models.
- [llm/](src/medassist/llm/): asynchronous provider contract, without inference.
- [retrieval/](src/medassist/retrieval/) and [services/](src/medassist/services/):
  reserved for later checkpoints.

Uvicorn imports `medassist.main:app`, which calls the application factory and
validates configuration. For programmatic use, import `create_app` from
`medassist.application`; importing the factory does not load settings. Each app
owns its settings, and FastAPI injects them into the health handler. The handler
returns a small public response schema without exposing configuration secrets.

## Validation

```powershell
uv run pytest -v
uv run ruff check .
uv run ruff format --check .
```

Tests use FastAPI's in-memory `TestClient`, discard inherited `MEDASSIST_` settings,
and use temporary working directories. They do not contact external services or
require credentials. Dependency installation is separate from test execution;
after sync, `uv run --offline pytest -v` also runs the suite without registry access.

Checkpoint 2 is PubMed retrieval and requires review and approval before work starts.
