from pathlib import Path

from enums import Environment

APP_ENV: Environment = Environment.LOCAL
APP_VERSION: str = "0.0.0"
FALLBACK_LOCALE: str = "en-US"

COMPONENTS_PATH = Path("server", "components")
"""The path to the directory containing the components."""
