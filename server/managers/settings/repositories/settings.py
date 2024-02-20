from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from server.database import DatabaseInterface
from server.utils.supports import Collection

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

    async def get(self, session: AsyncSession | None = None) -> Collection[Setting]:
        """
        Get all settings.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[Setting]
            The settings.
        """
        stmt = select(Setting)

        if session is not None:
            results = await session.execute(stmt)
        else:
            async with self._db.session() as session:
                results = await session.execute(stmt)

        return Collection(results.scalars().all())

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
        self, settings: Iterable[Setting], session: AsyncSession | None = None
    ) -> Collection[Setting]:
        """
        Create multiple settings.

        Parameters
        ----------
        settings : Iterable[Setting]
            The settings to create.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[Setting]
            The created settings.
        """
        if session is not None:
            session.add_all(settings)
            await session.flush()
            return Collection(settings)

        async with self._db.session() as session:
            session.add_all(settings)
            await session.flush()
            await session.commit()
            return Collection(settings)

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
        self, settings: Iterable[Setting], session: AsyncSession | None = None
    ) -> Collection[Setting]:
        """
        Overwrite all settings.

        Parameters
        ----------
        settings : Iterable[Setting]
            The settings to overwrite.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[Setting]
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
