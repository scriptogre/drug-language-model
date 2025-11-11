import re


# SQL Validation Functions
# -------------------------

def is_safe_query(sql: str) -> tuple[bool, str]:
    """
    Validate that SQL query is safe (SELECT only).

    Args:
        sql: SQL query to validate

    Returns:
        Tuple of (is_safe, error_message)
        - (True, "") if query is safe
        - (False, "error message") if query is dangerous
    """
    # List of dangerous SQL keywords
    dangerous_keywords = [
        r'\bINSERT\b',
        r'\bUPDATE\b',
        r'\bDELETE\b',
        r'\bDROP\b',
        r'\bALTER\b',
        r'\bCREATE\b',
        r'\bTRUNCATE\b',
        r'\bREPLACE\b',
        r'\bMERGE\b',
    ]

    # Check for dangerous keywords (case-insensitive)
    for keyword_pattern in dangerous_keywords:
        if re.search(keyword_pattern, sql, re.IGNORECASE):
            keyword = keyword_pattern.strip(r'\b').strip(r'\\')
            return (
                False,
                f"Query rejected for security reasons. Only SELECT queries are allowed. "
                f"Found dangerous keyword: {keyword}"
            )

    return (True, "")


def extract_sql_from_text(text: str) -> str:
    """
    Extract SQL from text, removing markdown code blocks if present.

    Args:
        text: Text potentially containing SQL with markdown

    Returns:
        Clean SQL query
    """
    # Remove ```sql and ``` markers if present
    pattern = r'```(?:sql)?\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

    if match:
        return match.group(1).strip()

    return text.strip()
