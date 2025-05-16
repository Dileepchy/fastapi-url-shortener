import shortuuid
from typing import Dict, Optional
from fastapi import HTTPException, status

# --- In-Memory Storage (Demonstration purposes only - NOT suitable for production) ---
# In-memory dictionary to store the mapping of short codes to long URLs.
# This violates 12-Factor Principles IV (Backing Services) and VI (Processes)
# because state is coupled to the process and not externalized.
# A real-world app would use Redis, PostgreSQL, etc.
url_database: Dict[str, str] = {}

def generate_short_code() -> str:
    """Generates a unique short code."""
    # shortuuid generates a unique ID combining timestamp and random number.
    # Default alphabet is suitable for URLs.
    return shortuuid.uuid()[:8] # Use first 8 characters for brevity

def add_url(long_url: str) -> str:
    """Adds a long URL to the store and returns the generated short code."""
    # In a real app, you'd check if the long_url already exists to return
    # the same short code, but for simplicity, we'll generate a new one every time.
    short_code = generate_short_code()
    # Basic collision avoidance loop (highly unlikely with shortuuid)
    while short_code in url_database:
         short_code = generate_short_code()

    url_database[short_code] = long_url
    return short_code

def get_url(short_code: str) -> Optional[str]:
    """Retrieves the long URL associated with a short code."""
    return url_database.get(short_code)

# --- Note for future improvement ---
# To comply with 12-Factor, this store logic would be replaced by
# interactions with an external database or cache like Redis, configured
# via environment variables.