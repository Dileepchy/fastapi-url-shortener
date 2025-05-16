from pydantic import BaseModel, HttpUrl

class URLShortenRequest(BaseModel):
    """Model for the request body when shortening a URL."""
    long_url: HttpUrl # Ensures the input is a valid URL

class URLShortenResponse(BaseModel):
    """Model for the response when a URL is shortened."""
    long_url: str
    short_code: str
    short_url: str # The full short URL