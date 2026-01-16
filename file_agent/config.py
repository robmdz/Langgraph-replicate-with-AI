"""Configuration management for the File Agent application."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


class Config:
    """Manages application configuration and environment variables.

    This class handles loading and managing configuration settings from environment
    variables and .env files. It provides validation and access to configuration
    values throughout the application.

    Attributes:
        openai_api_key: OpenAI API key for authentication. Loaded from
            OPENAI_API_KEY environment variable. Required for operation.
        openai_model: OpenAI model to use (e.g., "gpt-4o", "gpt-4"). Loaded from
            OPENAI_MODEL environment variable, defaults to "gpt-4o".
        max_file_size: Maximum file size in bytes. Loaded from MAX_FILE_SIZE
            environment variable, defaults to 10485760 (10MB).
    """

    def __init__(self) -> None:
        """Initialize configuration by loading environment variables.

        Loads configuration from environment variables, with support for .env files.
        Checks multiple locations for .env file in this order:
        1. Current working directory (.env)
        2. Home directory (~/.env)
        3. Project directory (where file_agent package is located)

        Environment variables take precedence over .env file values.

        Note:
            The .env file is loaded from multiple locations to support global usage.
            Environment variables set in the shell take precedence over .env file values.
        """
        # Try to load .env file from multiple locations (in order of precedence)
        env_paths = [
            Path.cwd() / ".env",  # Current working directory
            Path.home() / ".env",  # Home directory
            Path(__file__).parent.parent / ".env",  # Project root directory
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                break  # Use the first .env file found

        self.openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
        self.openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o")
        self.max_file_size: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB default

    def validate(self) -> None:
        """Validate that required configuration is present.

        Checks that all required configuration values are set. Currently, only
        the OpenAI API key is required. Other settings have defaults.

        Raises:
            ValueError: If OPENAI_API_KEY is not set. The error message includes
                instructions on how to set the API key via environment variable
                or .env file.

        Note:
            This method should be called before using the agent to ensure all
            required configuration is present. It's automatically called by
            create_agent() in the agent module.
        """
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is not set. Please set it in your environment "
                "or create a .env file with OPENAI_API_KEY=your_key_here"
            )

    def get_openai_api_key(self) -> str:
        """Get the OpenAI API key.

        Retrieves the OpenAI API key from configuration. This method provides
        a safe way to access the API key with validation.

        Returns:
            The OpenAI API key as a string.

        Raises:
            ValueError: If OPENAI_API_KEY is not configured. This ensures that
                the API key is always present when needed.

        Note:
            This method should be used instead of directly accessing
            self.openai_api_key to ensure the key is validated before use.
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not configured")
        return self.openai_api_key


# Global configuration instance
config = Config()
