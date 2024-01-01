from constants import SQLITE_FILE_NAME
from database.models import setting  # noqa
from sqlalchemy import create_engine

sqlite_file_name = SQLITE_FILE_NAME
sqlite_url = f"sqlite:///{sqlite_file_name}"

sqlite_engine = create_engine(sqlite_url, echo=True)
