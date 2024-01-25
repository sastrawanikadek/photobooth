from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from server.database import DatabaseInterface

from ..models import Setting


class SettingsRepository:
    """
    Repository for settings.

    Attributes
    ----------
    _db : DatabaseInterface
        The database.
    """

    def __init__(self, db: DatabaseInterface) -> None:
        """
        Initialize the repository.

        Parameters
        ----------
        db : DatabaseInterface
            The database.
        """
        self._db = db

    async def get(self) -> Sequence[Setting]:
        """
        Get all settings.

        Returns
        -------
        Sequence[Setting]
            The settings.
        """
        async with self._db.session() as session:
            stmt = select(Setting)
            results = await session.execute(stmt)
            settings: Sequence[Setting] = results.scalars().all()
            return settings

    async def create(
        self, setting: Setting, session: AsyncSession | None = None
    ) -> Setting:
        """
        Create a new setting.

        Parameters
        ----------
        setting : Setting
            The setting to create.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Setting
            The created setting.
        """
        if session is not None:
            session.add(setting)
            await session.flush()
            return setting

        async with self._db.session() as session:
            session.add(setting)
            await session.flush()
            await session.commit()
            return setting

    async def create_many(
        self, settings: Sequence[Setting], session: AsyncSession | None = None
    ) -> Sequence[Setting]:
        """
        Create multiple settings.

        Parameters
        ----------
        settings : Sequence[Setting]
            The settings to create.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Sequence[Setting]
            The created settings.
        """
        if session is not None:
            session.add_all(settings)
            await session.flush()
            return settings

        async with self._db.session() as session:
            session.add_all(settings)
            await session.flush()
            await session.commit()
            return settings

    async def truncate(self, session: AsyncSession | None = None) -> None:
        """
        Truncate the settings table.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.
        """
        if session is not None:
            await session.execute(SQLModel.metadata.tables["settings"].delete())
            return

        async with self._db.session() as session:
            await session.execute(SQLModel.metadata.tables["settings"].delete())
            await session.commit()

    async def overwrite(
        self, settings: Sequence[Setting], session: AsyncSession | None = None
    ) -> Sequence[Setting]:
        """
        Overwrite all settings.

        Parameters
        ----------
        settings : Sequence[Setting]
            The settings to overwrite.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Sequence[Setting]
            The overwritten settings.
        """
        if session is not None:
            await self.truncate(session)
            return await self.create_many(settings, session)

        async with self._db.session() as session:
            await self.truncate(session)
            settings = await self.create_many(settings, session)
            await session.commit()

            return settings
