from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


class DatabaseInterface(ABC):
    """Interface for database implementations."""

    @abstractmethod
    def __init__(self, connection_string: str) -> None:
        """
        Initialize the database.

        Parameters
        ----------
        connection_string : str
            The connection string of the database.
        """

    @property
    @abstractmethod
    def engine(self) -> AsyncEngine:
        """Get the database engine."""

    @property
    @abstractmethod
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Get the database session factory."""

    @abstractmethod
    async def close(self) -> None:
        """Close the database connection and release resources."""
