"""
Unified LLM module using LiteLLM for provider abstraction.
"""
import re
from litellm import completion

from app.config import settings


def _extract_sql(text: str) -> str:
    """
    Extract SQL from text, removing markdown code blocks if present.

    Args:
        text: Text potentially containing SQL with markdown

    Returns:
        Clean SQL query
    """
    pattern = r'```(?:sql)?\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return text.strip()


def _build_sql_prompt(question: str, schema_context: str) -> str:
    """Build the prompt for SQL generation."""
    return f"""You are a PostgreSQL SQL expert. Generate a SQL query for the following question.

Database: DrugCentral PostgreSQL database
Schema information:
{schema_context}

User question: {question}

Instructions:
- Return ONLY a valid PostgreSQL SELECT query
- Do not include explanations or markdown formatting
- Use proper PostgreSQL syntax
- Limit results to 1000 rows with LIMIT clause
- Return the SQL query directly without any wrapper text

SQL Query:"""


def _build_answer_prompt(question: str, sql_query: str, query_results: dict) -> str:
    """Build the prompt for generating a natural language answer."""
    columns = query_results.get("columns", [])
    rows = query_results.get("rows", [])
    row_count = query_results.get("row_count", 0)

    results_text = f"Number of results: {row_count}\n\n"

    if row_count > 0:
        results_text += "Columns: " + ", ".join(columns) + "\n\n"
        results_text += "Results:\n"

        max_rows = min(20, len(rows))
        for i, row in enumerate(rows[:max_rows], 1):
            row_dict = dict(zip(columns, row))
            results_text += f"{i}. {row_dict}\n"

        if row_count > max_rows:
            results_text += f"\n... and {row_count - max_rows} more results"

    return f"""You are a helpful assistant explaining database query results to a user.

User's Question: {question}

SQL Query Executed:
{sql_query}

Query Results:
{results_text}

Instructions:
- Provide a BRIEF answer (2-3 sentences maximum) based ONLY on the query results above
- State the number of results found and provide a high-level summary
- If multiple results exist, do NOT list individual items - instead tell the user to "view the complete list in the table below"
- For single results, you may briefly describe the finding
- If the results are empty, explain that no matching data was found
- Do NOT provide information not present in the query results
- Do NOT provide medical advice or recommendations
- Do NOT speculate beyond the data provided
- Do NOT use markdown formatting (no asterisks, no bold, no italics) - write in plain text only
- Keep your answer SHORT and direct the user to the detailed results table below

Answer:"""


async def generate_sql(question: str, schema_context: str) -> tuple[str, dict]:
    """
    Generate SQL query from natural language question using LiteLLM.

    Args:
        question: User's natural language question
        schema_context: Database schema information

    Returns:
        Tuple of (Generated SQL query string, usage dict with token counts)

    Raises:
        Exception: If API call fails or returns invalid response
    """
    try:
        prompt = _build_sql_prompt(question, schema_context)

        response = completion(
            model=settings.SQL_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
        )

        sql = response.choices[0].message.content.strip()
        sql = _extract_sql(sql)

        usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "model": settings.SQL_MODEL
        }

        return sql, usage

    except Exception as e:
        raise Exception(f"LLM API error: {str(e)}")


async def generate_answer(question: str, sql_query: str, query_results: dict) -> tuple[str, dict]:
    """
    Generate a natural language answer based on query results using LiteLLM.

    Args:
        question: User's original natural language question
        sql_query: The SQL query that was executed
        query_results: Dictionary containing columns, rows, and row_count

    Returns:
        Tuple of (Natural language answer string, usage dict with token counts)

    Raises:
        Exception: If API call fails or returns invalid response
    """
    try:
        prompt = _build_answer_prompt(question, sql_query, query_results)

        response = completion(
            model=settings.ANSWER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
        )

        answer = response.choices[0].message.content.strip()

        usage = {
            "input_tokens": response.usage.prompt_tokens,
            "output_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
            "model": settings.ANSWER_MODEL
        }

        return answer, usage

    except Exception as e:
        raise Exception(f"LLM API error while generating answer: {str(e)}")
