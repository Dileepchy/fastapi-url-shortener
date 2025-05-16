from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
import logging

# Import local modules
from . import models, config, store

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="12-Factor FastAPI URL Shortener",
    description="A simple URL shortening service built with FastAPI, demonstrating 12-Factor App principles.",
    version="1.0.0"
)

# Dependency to get settings
def get_settings():
    return config.settings

# In-memory store (dependency injection placeholder, though it's a global dict here)
# In a real app, this would be a connection to an external service.
def get_url_store():
    return store # Return the module or a store instance

@app.get("/", include_in_schema=False)
async def root():
    """Redirects root to the API documentation."""
    return RedirectResponse(url="/docs")

@app.post("/shorten", response_model=models.URLShortenResponse)
async def create_short_url(
    url_request: models.URLShortenRequest,
    settings: config.Settings = Depends(get_settings),
    url_store = Depends(get_url_store) # Use dependency injection
):
    """
    Creates a short code for a given long URL.
    """
    logger.info(f"Received request to shorten: {url_request.long_url}")
    short_code = url_store.add_url(str(url_request.long_url))

    # Construct the full short URL (using config settings if available)
    # This is a simplified approach. In a real app, you might use a request context.
    base_url = f"http://localhost:{settings.APP_PORT}" # Default
    # If you added BASE_URL to settings:
    # base_url = settings.BASE_URL if settings.BASE_URL else f"http://localhost:{settings.APP_PORT}"

    short_url = f"{base_url}/{short_code}"

    logger.info(f"Shortened {url_request.long_url} to {short_url} (code: {short_code})")

    return models.URLShortenResponse(
        long_url=url_request.long_url,
        short_code=short_code,
        short_url=short_url
    )

@app.get("/{short_code}")
async def redirect_to_long_url(
    short_code: str,
    url_store = Depends(get_url_store) # Use dependency injection
):
    """
    Redirects a short code to the original long URL.
    """
    logger.info(f"Received request for short code: {short_code}")
    long_url = url_store.get_url(short_code)

    if long_url is None:
        logger.warning(f"Short code not found: {short_code}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short code not found")

    logger.info(f"Redirecting {short_code} to {long_url}")
    return RedirectResponse(url=long_url)

# You could add more endpoints (e.g., GET all, DELETE) but keep it simple for the assignment.