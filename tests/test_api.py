import pytest
from fastapi.testclient import TestClient
from app.main import app # Import the FastAPI app instance
from app.store import url_database # Access the in-memory store for verification

# Use the TestClient for making requests to the FastAPI app
client = TestClient(app)

# Define a fixture to clear the in-memory database before each test
# This ensures tests are isolated and don't affect each other.
@pytest.fixture(autouse=True)
def clear_database():
    """Clears the in-memory database before each test."""
    url_database.clear()
    yield # This allows the test to run
    # You could add cleanup after the test here if needed, but clear is enough.

def test_create_short_url():
    """Test creating a new short URL."""
    long_url = "https://www.example.com/very/long/url/path"
    response = client.post("/shorten", json={"long_url": long_url})

    assert response.status_code == 200
    data = response.json()

    assert "long_url" in data
    assert data["long_url"] == long_url
    assert "short_code" in data
    assert isinstance(data["short_code"], str)
    assert len(data["short_code"]) > 0 # Short code should not be empty
    assert "short_url" in data
    assert isinstance(data["short_url"], str)
    assert data["short_code"] in data["short_url"] # Short code should be part of the short URL

    # Verify it was added to the in-memory database
    assert data["short_code"] in url_database
    assert url_database[data["short_code"]] == long_url

def test_redirect_to_long_url():
    """Test redirecting from a short code to the long URL."""
    # Manually add a URL to the in-memory store for testing redirection
    short_code = "testcode"
    long_url = "https://www.anothersite.org/target"
    url_database[short_code] = long_url

    response = client.get(f"/{short_code}")

    # Check for a redirect response
    assert response.status_code == 307 # Temporary Redirect (FastAPI default)
    assert response.headers["location"] == long_url

def test_redirect_not_found():
    """Test requesting a short code that does not exist."""
    non_existent_code = "nonexistent"
    response = client.get(f"/{non_existent_code}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Short code not found"}

def test_invalid_long_url_input():
    """Test sending an invalid URL format to the shorten endpoint."""
    invalid_url = "not a url"
    response = client.post("/shorten", json={"long_url": invalid_url})

    assert response.status_code == 422 # Unprocessable Entity (Pydantic validation error)
    data = response.json()
    assert "detail" in data
    assert any("value is not a valid URL" in error["msg"] for error in data["detail"])