from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    APP_PORT: int = 8000 # Default port

    # model_config = SettingsConfigDict(env_file='.env', extra='ignore') # Use this line if you explicitly want to load .env file

# Create a settings instance to be used throughout the app
settings = Settings()