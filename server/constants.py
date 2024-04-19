from pathlib import Path
from uuid import UUID

from .enums import Environment

APP_ENV: Environment = Environment.LOCAL
APP_VERSION: str = "0.0.0"
APP_UUID_NAMESPACE: UUID = UUID("a14072d6-89f9-48c3-b177-e197f4c9f694")

DATABASE_CONNECTION_STRING: str = "sqlite+aiosqlite:///database.db"
FALLBACK_LOCALE: str = "en-US"

COMPONENTS_PATH = Path("server", "components")
"""The path to the directory containing the components."""

SETTING_STORAGE_PROVIDER = "storage_provider"
"""The provider for the storage of captured images."""

SETTING_STORAGE_PROVIDER_API_KEY = "storage_api_key"
"""The API key for the storage provider."""

STORAGES_PATH = Path("server", "storages")
"""The path to the directory containing the file storages."""

APP_STORAGE_PATH = STORAGES_PATH / "app"
"""The path to the directory containing the application files."""

LOGS_STORAGE_PATH = STORAGES_PATH / "logs"
"""The path to the directory containing the logs."""

PUBLIC_STORAGE_PATH = APP_STORAGE_PATH / "public"
"""The path to the directory containing the public files."""
