from contextlib import asynccontextmanager
from typing import AsyncIterator, Generic, Iterable, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel, select

from server.utils.supports.collection import Collection

from .contexts import request_session
from .interfaces import DatabaseInterface

_T = TypeVar("_T", bound="SQLModel")


class Repository(Generic[_T]):
    """Base class for repositories."""

    def __init__(self, db: DatabaseInterface, model_cls: type[_T]) -> None:
        """
        Initialize the repository.

        Parameters
        ----------
        db : DatabaseInterface
            The database.
        model_cls : type[DBModel]
            The model class.
        """
        self.db = db
        self._model_cls = model_cls

    async def get(self, session: AsyncSession | None = None) -> Collection[_T]:
        """
        Get all records from the database.

        Parameters
        ----------
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[_T]
            The records.
        """
        stmt = select(self._model_cls)

        async with self.get_session(session) as db_session:
            results = await db_session.execute(stmt)

        return Collection(results.scalars().all())

    async def create(self, model: _T, session: AsyncSession | None = None) -> _T:
        """
        Create a record in the database.

        Parameters
        ----------
        model : DBModel
            The model to create.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        DBModel
            The created model.
        """
        async with self.get_session(session) as db_session:
            db_session.add(model)
            await db_session.flush()

        return model

    async def create_many(
        self, models: Iterable[_T], session: AsyncSession | None = None
    ) -> Collection[_T]:
        """
        Create multiple records in the database.

        Parameters
        ----------
        models : Iterable[DBModel]
            The models to create.
        session : AsyncSession | None
            The database session.

        Returns
        -------
        Collection[DBModel]
            The created models.
        """
        async with self.get_session(session) as db_session:
            db_session.add_all(models)
            await db_session.flush()

        return Collection(models)

    async def update(self, model: _T, session: AsyncSession | None = None) -> _T:
        """
        Update a record in the database.

        Parameters
        ----------
        model : DBModel
            The model to update.

        Returns
        -------
        DBModel
            The updated model.
        """
        async with self.get_session(session) as db_session:
            db_session.add(model)
            await db_session.flush()

        return model

    @asynccontextmanager
    async def get_session(
        self, outer_session: AsyncSession | None = None
    ) -> AsyncIterator[AsyncSession]:
        """
        Get the database session.

        Parameters
        ----------
        outer_session : AsyncSession | None
            The outer session.
        """
        if outer_session is not None:
            session = outer_session
            managed_session = False
        else:
            current_request_session = request_session.get()
            session = current_request_session or self.db.session_factory()
            managed_session = current_request_session is None

        try:
            if managed_session:
                await session.begin()

            yield session
        except Exception:
            if managed_session:
                await session.rollback()
        else:
            if managed_session:
                await session.commit()
        finally:
            if managed_session:
                await session.close()
