from typing import Iterable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from server.database import DatabaseInterface
from server.utils.supports.collection import Collection

from ..models import BackupSetting, Setting


class BackupSettingsRepository:
    """
    Backup settings repository.

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

    async def get(
        self, session: AsyncSession | None = None
    ) -> Collection[BackupSetting]:
        """
        Get all backup settings.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[BackupSetting]
            The backup settings.
        """
        stmt = select(BackupSetting)

        if session is not None:
            results = await session.execute(stmt)
        else:
            async with self._db.session() as session:
                results = await session.execute(stmt)

        return Collection(results.scalars().all())

    async def create_many(
        self, settings: Iterable[BackupSetting], session: AsyncSession | None = None
    ) -> Collection[BackupSetting]:
        """
        Create multiple settings.

        Parameters
        ----------
        settings : Iterable[BackupSetting]
            The settings to create.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[BackupSetting]
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
        Truncate the backup settings table.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.
        """
        if session is not None:
            await session.execute(SQLModel.metadata.tables["backup_settings"].delete())
            return

        async with self._db.session() as session:
            await session.execute(SQLModel.metadata.tables["backup_settings"].delete())
            await session.commit()

    async def backup(
        self, settings: Iterable[Setting], session: AsyncSession | None = None
    ) -> None:
        """
        Backup the settings table.

        Parameters
        ----------
        settings : Iterable[Setting]
            The settings to backup.
        session : AsyncSession | None
            The database session.
        """
        backup_settings = [
            BackupSetting(**setting.model_dump()) for setting in settings
        ]

        if session is not None:
            await self.truncate(session=session)
            await self.create_many(backup_settings, session=session)
            return

        async with self._db.session() as session:
            await self.truncate(session=session)
            await self.create_many(backup_settings, session=session)
            await session.commit()

    async def restore(self, session: AsyncSession | None = None) -> Collection[Setting]:
        """
        Restore the settings data from the backup.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[Setting]
            The restored settings.
        """
        backup_settings = await self.get(session)
        settings = backup_settings.map(lambda args: Setting(**args[0].model_dump()))

        return settings
