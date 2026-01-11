"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from file_agent.config import Config


class TestConfig:
    """Tests for Config class."""

    def test_config_defaults(self) -> None:
        """Test default configuration values."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            assert config.openai_model == "gpt-4o"
            assert config.max_file_size == 10485760  # 10MB

    def test_config_from_env(self) -> None:
        """Test loading configuration from environment variables."""
        with patch.dict(
            os.environ,
            {
                "OPENAI_API_KEY": "test-key-123",
                "OPENAI_MODEL": "gpt-4",
                "MAX_FILE_SIZE": "5242880",
            },
            clear=True,
        ):
            config = Config()
            assert config.openai_api_key == "test-key-123"
            assert config.openai_model == "gpt-4"
            assert config.max_file_size == 5242880

    def test_validate_missing_api_key(self) -> None:
        """Test validation fails when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                config.validate()

    def test_get_openai_api_key(self) -> None:
        """Test getting OpenAI API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}, clear=True):
            config = Config()
            assert config.get_openai_api_key() == "test-key"

    def test_get_openai_api_key_missing(self) -> None:
        """Test getting API key when it's not set."""
        with patch.dict(os.environ, {}, clear=True):
            config = Config()
            with pytest.raises(ValueError, match="OPENAI_API_KEY"):
                config.get_openai_api_key()
