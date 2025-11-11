import re
from tortoise import Tortoise


async def execute_raw_query(sql: str) -> dict:
    """
    Execute raw SQL query with timeout and row limit.

    Args:
        sql: SQL query to execute

    Returns:
        Dict with columns, rows, and row_count

    Raises:
        Exception: If query execution fails
    """
    conn = Tortoise.get_connection("default")

    # Add LIMIT 1000 if not present
    if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
        sql = sql.rstrip(';') + ' LIMIT 1000'

    # Set statement timeout to 30 seconds
    await conn.execute_query("SET statement_timeout = '30s'")

    try:
        # Execute the query
        result = await conn.execute_query_dict(sql)

        if not result:
            return {
                "columns": [],
                "rows": [],
                "row_count": 0
            }

        # Extract column names from first row
        columns = list(result[0].keys()) if result else []

        # Convert rows to list of tuples
        rows = [tuple(row.values()) for row in result]

        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows)
        }
    finally:
        # Reset statement timeout
        await conn.execute_query("RESET statement_timeout")


async def get_schema_info() -> str:
    """
    Get comprehensive schema information for Gemini context.

    Returns:
        Formatted string with comprehensive schema documentation
    """
    from app.schema_docs import get_schema_context

    # Return the comprehensive schema documentation
    return get_schema_context()
