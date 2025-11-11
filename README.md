# DrugCentral Query Interface

Ask questions about drugs in plain English, get answers powered by AI + real pharmaceutical data.

## What This Does

This app lets you query the DrugCentral pharmaceutical database using natural language. Type "What drugs treat diabetes?" and it converts your question to SQL, runs it against PostgreSQL, and gives you a human-readable answer.

**Tech Stack:**
- Backend: FastAPI (Python 3.13)
- Database: PostgreSQL 17 with DrugCentral dataset
- AI: Google Gemini (converts English → SQL)
- Frontend: HTMX + Tailwind CSS

## Setup

### Prerequisites
- Docker & Docker Compose
- Google API key (for Gemini AI) - get one at [Google AI Studio](https://aistudio.google.com/app/apikey)

### Quick Start

1. **Clone and navigate to project**
   ```bash
   cd drugcentral
   ```

2. **Create `.env` from `.env.example`, and update `GOOGLE_API_KEY`**:
   ```bash
   cp .env.example .env
   ```

3. **Download `drugcentral.dump.<version>.sql.gz` [here](https://drugcentral.org/ActiveDownload)**
4. **Copy the `.sql.gz` file to `data/` directory**
5. **Start everything**
   ```bash
   docker compose up
   ```

6. **Open browser**
   ```
   http://localhost:8000
   ```

That's it. The database automatically loads automatically on first run.

## How It Works

```
You type: "What drugs treat migraines?"
         ↓
Gemini AI generates SQL query
         ↓
PostgreSQL executes query
         ↓
Gemini formats results in plain English
         ↓
You see: Human answer + data table + SQL used
```

## Example Queries

- "What drugs are approved for treating hypertension?"
- "Show me all drugs that target the dopamine receptor"
- "What are the side effects of aspirin?"
- "List drugs approved by FDA in 2020"

## Troubleshooting

- **Port 8000 already in use:** Change port in docker-compose.yml
- **Database connection fails:** Check PostgreSQL is running and .env credentials match
- **AI not responding:** Verify GOOGLE_API_KEY is valid
- **Slow queries:** Check data/README.txt for database optimization tips
