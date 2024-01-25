from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from server.database import DatabaseInterface

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

    async def get(self, session: AsyncSession | None = None) -> Sequence[BackupSetting]:
        """
        Get all backup settings.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Sequence[BackupSetting]
            The backup settings.
        """
        if session is not None:
            stmt = select(BackupSetting)
            results = await session.execute(stmt)
            backup_settings: Sequence[BackupSetting] = results.scalars().all()
            return backup_settings

        async with self._db.session() as session:
            stmt = select(BackupSetting)
            results = await session.execute(stmt)
            backup_settings = results.scalars().all()
            return backup_settings

    async def create_many(
        self, settings: Sequence[BackupSetting], session: AsyncSession | None = None
    ) -> Sequence[BackupSetting]:
        """
        Create multiple settings.

        Parameters
        ----------
        settings : Sequence[BackupSetting]
            The settings to create.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Sequence[BackupSetting]
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
        self, settings: Sequence[Setting], session: AsyncSession | None = None
    ) -> None:
        """
        Backup the settings table.

        Parameters
        ----------
        settings : Sequence[Setting]
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

    async def restore(self, session: AsyncSession | None = None) -> Sequence[Setting]:
        """
        Restore the settings data from the backup.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Sequence[Setting]
            The restored settings.
        """
        backup_settings = await self.get(session)

        settings = [
            Setting(**backup_setting.model_dump()) for backup_setting in backup_settings
        ]

        return settings
