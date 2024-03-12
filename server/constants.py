from pathlib import Path

from .enums import Environment

APP_ENV: Environment = Environment.LOCAL
APP_VERSION: str = "0.0.0"
DATABASE_CONNECTION_STRING: str = "sqlite+aiosqlite:///database.db"
FALLBACK_LOCALE: str = "en-US"

COMPONENTS_PATH = Path("server", "components")
"""The path to the directory containing the components."""

SETTING_STORAGE_PROVIDER = "storage_provider"
"""The provider for the storage of captured images."""

SETTING_STORAGE_PROVIDER_API_KEY = "storage_api_key"
"""The API key for the storage provider."""
