from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form
from jinja2_fragments.fastapi import Jinja2Blocks
from tortoise import Tortoise

from app.schema_docs import SCHEMA_OVERVIEW
from app.utils import extract_sql_from_text, is_safe_query
from app.config import settings
from app.db import execute_raw_query
from app.gemini import generate_sql, generate_answer



# FastAPI Application
# -------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    await Tortoise.init(config=settings.TORTOISE_ORM)

    yield

    # Shutdown
    await Tortoise.close_connections()


app = FastAPI(title="DrugCentral Query Interface", lifespan=lifespan)

# Initialize templates
templates = Jinja2Blocks(directory=str(settings.TEMPLATES_DIR))


@app.get("/")
async def index(request: Request):
    """Render the main query page."""
    return templates.TemplateResponse(request, "index.html", {"question": ""})


@app.post("/query")
async def submit_query(request: Request, question: str = Form(...)):
    """
    Handle question submission and return results.

    Args:
        request: FastAPI request object
        question: User's natural language question

    Returns:
        HTMLResponse with results or error
    """
    try:
        # Validate question length
        if not question or len(question) > 500:
            return templates.TemplateResponse(
                request,
                "index.html",
                {
                    "error": "Please enter a question between 1 and 500 characters.",
                    "question": question
                },
                block_name="results"
            )

        # Generate SQL using Gemini
        import time
        start_time = time.time()
        print(f"[DEBUG] Starting Gemini API call for question: {question[:50]}...")
        raw_sql = await generate_sql(question, SCHEMA_OVERVIEW)
        elapsed = time.time() - start_time
        print(f"[DEBUG] Gemini API call completed in {elapsed:.2f}s")

        # Extract SQL from potential markdown
        sql = extract_sql_from_text(raw_sql)

        # Validate SQL safety
        is_safe, error_msg = is_safe_query(sql)
        if not is_safe:
            return templates.TemplateResponse(
                request,
                "index.html",
                {
                    "error": error_msg,
                    "question": question,
                    "generated_sql": sql  # Show the rejected SQL
                },
                block_name="results"
            )

        # Execute query
        result = await execute_raw_query(sql)

        # Generate natural language answer
        print(f"[DEBUG] Generating natural language answer...")
        answer_start_time = time.time()
        llm_answer = await generate_answer(question, sql, result)
        answer_elapsed = time.time() - answer_start_time
        print(f"[DEBUG] Answer generation completed in {answer_elapsed:.2f}s")

        # Render results
        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "columns": result["columns"],
                "rows": result["rows"],
                "row_count": result["row_count"],
                "question": question,
                "generated_sql": sql,  # Show the executed SQL
                "llm_answer": llm_answer  # Show the AI-generated answer
            },
            block_name="results"
        )

    except Exception as e:
        # Handle any errors
        error_message = str(e)
        print(f"[ERROR] Exception occurred: {error_message}")
        import traceback
        traceback.print_exc()

        # Provide user-friendly error messages
        if "Gemini API error" in error_message or "google.api_core" in error_message:
            error_message = "The AI service is currently unavailable. Please try again in a moment."
        elif "statement timeout" in error_message.lower():
            error_message = "Your query took too long to execute. Try asking a more specific question."
        elif "connection" in error_message.lower():
            error_message = "Database connection error. Please try again."
        elif "API key" in error_message or "authentication" in error_message.lower():
            error_message = "API authentication failed. Please check your Gemini API key configuration."
        else:
            error_message = f"Unable to execute query. Please try rephrasing your question. (Debug: {str(e)[:100]})"

        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "error": error_message,
                "question": question
            },
            block_name="results"
        )
