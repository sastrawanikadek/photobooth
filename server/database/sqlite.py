from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from server.constants import APP_ENV

from .interfaces import DatabaseInterface


class SQLiteDatabase(DatabaseInterface):
    """
    SQLite database implementation.

    Attributes
    ----------
    _connection_string : str
        The connection string of the database.
    _engine : AsyncEngine | None
        The database engine.
    _session_factory : async_sessionmaker[AsyncSession] | None
        The database session.
    """

    _connection_string: str
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    def __init__(self, connection_string: str) -> None:
        """
        Initialize the database.

        Parameters
        ----------
        connection_string : str
            The connection string of the database.
        """
        self._connection_string = connection_string

    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine."""
        if self._engine is None:
            self._engine = create_async_engine(
                self._connection_string, echo=APP_ENV.is_debug
            )
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the database session factory."""
        if self._session_factory is None:
            self._session_factory = async_sessionmaker(
                self.engine, expire_on_commit=False
            )
        return self._session_factory

    async def close(self) -> None:
        """Close the database connection and release resources."""
        if self._session_factory is not None:
            await self._session_factory().close_all()
            self._session_factory = None

        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
