"""Configuration management for the File Agent application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Manages application configuration and environment variables."""

    def __init__(self) -> None:
        """Initialize configuration by loading environment variables."""
        # Load .env file if it exists
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            load_dotenv(env_path)

        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default

    def validate(self) -> None:
        """Validate that required configuration is present.

        Raises:
            ValueError: If required configuration is missing.
        """
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please set it in your environment "
                "or create a .env file with OPENAI_API_KEY=your_key_here"
            )

    def get_openai_api_key(self) -> str:
        """Get the OpenAI API key.

        Returns:
            The OpenAI API key.

        Raises:
            ValueError: If the API key is not set.
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        return self.openai_api_key


# Global configuration instance
config = Config()
