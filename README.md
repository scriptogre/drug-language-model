# DrugCentral Query Interface

Natural language queries for pharmaceutical data using LLMs and SQL.

## What It Does

Query the DrugCentral database in plain English. An LLM converts your question to SQL, executes it against PostgreSQL, and returns human-readable answers.

**Stack:** FastAPI, PostgreSQL 17, LiteLLM (Anthropic/OpenAI/Google), HTMX, Tailwind

⚠️ **Heavy development** - API and features subject to change

## Getting Started

**Prerequisites:** Docker, API key (Anthropic/OpenAI/Google)

```bash
# Setup
cp .env.example .env         # Add your API key
just setup                    # Download database dump
just build                    # Build containers
just up                       # Start services

# Open http://localhost:8000
```

**Commands:**
- `just setup` - download DrugCentral database
- `just build` - build Docker images
- `just up` - start services
- `just down` - stop services
- `just logs` - view logs
- `just psql` - access database
