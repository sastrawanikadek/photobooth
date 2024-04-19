from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from server.database.interfaces import DatabaseInterface
from server.database.repository import Repository

from .models import Setting


class SettingsRepository(Repository[Setting]):
    """Repository for settings."""

    def __init__(self, db: DatabaseInterface) -> None:
        """
        Initialize the settings repository.

        Parameters
        ----------
        db : DatabaseInterface
            The database interface.
        """
        super().__init__(db, Setting)

    async def find_by_uuid(
        self, uuid: str, session: AsyncSession | None = None
    ) -> Optional[Setting]:
        """
        Find a setting by its UUID.

        Parameters
        ----------
        uuid : str
            The UUID of the setting.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Setting | None
            The setting, if found.
        """
        stmt = select(Setting).where(Setting.uuid == uuid)

        async with self.get_session(session) as db_session:
            result = await db_session.execute(stmt)

        setting: Optional[Setting] = result.scalars().first()
        return setting
