"""
Configuration module for environment variable validation and management.

Validates: Requirements 10.1, 10.2, 10.3, 10.4
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env from the project root (one level up from app/)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when required configuration is missing or invalid."""
    pass


class Config:
    """Application configuration with validation."""

    def __init__(self):
        """Initialize and validate configuration."""
        self._validate_required_variables()
        self._load_configuration()

    def _validate_required_variables(self):
        """
        Validate that all required environment variables are set.

        Validates: Requirements 10.4
        """
        required_vars = {
            "GOOGLE_CREDENTIALS_JSON": "Google service account credentials (JSON string)",
            "API_SECRET_KEY": "Secret key for API authentication",
            "ALLOWED_ORIGINS": "Comma-separated list of allowed CORS origins",
            "REGISTRATION_DATA_PATH": "Path to registration data JSON file",
            "ACCOMMODATION_SHEET_ID": "Google Sheet ID for accommodation data",
            "EVENTS_SHEET_ID": "Google Sheet ID for events registration",
            "WORKSHOPS_SHEET_ID": "Google Sheet ID for workshops registration",
            "VALEDICTION_SHEET_ID": "Google Sheet ID for valediction token tracking"
        }

        missing_vars = []
        for var_name, description in required_vars.items():
            value = os.getenv(var_name)
            if not value:
                missing_vars.append(f"  - {var_name}: {description}")

        if missing_vars:
            error_message = (
                "Missing required environment variables:\n" +
                "\n".join(missing_vars) +
                "\n\nPlease set these variables in your .env file or environment."
            )
            logger.error(error_message)
            raise ConfigurationError(error_message)

    def _load_configuration(self):
        """
        Load and parse configuration values.

        Validates: Requirements 10.1, 10.2, 10.3
        """
        # Google Sheets Configuration
        self.google_credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        self.accommodation_sheet_id = os.getenv("ACCOMMODATION_SHEET_ID")
        self.events_sheet_id = os.getenv("EVENTS_SHEET_ID")
        self.workshops_sheet_id = os.getenv("WORKSHOPS_SHEET_ID")
        self.valediction_sheet_id = os.getenv("VALEDICTION_SHEET_ID")

        # Validate Google credentials JSON format
        try:
            self.google_credentials = json.loads(self.google_credentials_json)
        except json.JSONDecodeError as e:
            error_message = (
                f"Invalid GOOGLE_CREDENTIALS_JSON format: {e}\n"
                "Please ensure the value is a valid JSON string."
            )
            logger.error(error_message)
            raise ConfigurationError(error_message)

        # API Security
        self.api_secret_key = os.getenv("API_SECRET_KEY")

        # Warn if using default/weak secret key
        if self.api_secret_key in ["your-secret-key-here-change-this-in-production", "test", "dev"]:
            logger.warning(
                "WARNING: Using a weak or default API_SECRET_KEY. "
                "Please use a strong random key in production!"
            )

        # CORS Configuration
        self.allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
        self.allowed_origins = [origin.strip()
                                for origin in self.allowed_origins if origin.strip()]

        # Registration Data
        self.registration_data_path = os.getenv("REGISTRATION_DATA_PATH")

        # Validate registration data file exists
        if not os.path.exists(self.registration_data_path):
            error_message = (
                f"Registration data file not found: {self.registration_data_path}\n"
                "Please ensure the file exists at the specified path."
            )
            logger.error(error_message)
            raise ConfigurationError(error_message)

        # Optional Configuration
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.log_level = os.getenv("LOG_LEVEL", "INFO")

        # Log configuration summary
        logger.info("Configuration loaded successfully:")
        logger.info(f"  - Environment: {self.environment}")
        logger.info(f"  - Log Level: {self.log_level}")
        logger.info(
            f"  - Accommodation Sheet ID: {self.accommodation_sheet_id}")
        logger.info(f"  - Events Sheet ID: {self.events_sheet_id}")
        logger.info(f"  - Workshops Sheet ID: {self.workshops_sheet_id}")
        logger.info(f"  - Valediction Sheet ID: {self.valediction_sheet_id}")
        logger.info(f"  - Registration Data: {self.registration_data_path}")
        logger.info(f"  - Allowed Origins: {', '.join(self.allowed_origins)}")


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.

    Returns:
        Config: The application configuration

    Raises:
        ConfigurationError: If configuration is invalid or missing
    """
    global _config
    if _config is None:
        _config = Config()
    return _config


def validate_config():
    """
    Validate configuration at application startup.

    This function should be called during application initialization
    to ensure all required configuration is present before starting
    the server.

    Validates: Requirements 10.4

    Raises:
        ConfigurationError: If configuration is invalid or missing
    """
    try:
        get_config()
        logger.info("✓ Configuration validation passed")
    except ConfigurationError as e:
        logger.error("✗ Configuration validation failed")
        raise
