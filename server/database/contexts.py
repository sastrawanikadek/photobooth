from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession

request_session: ContextVar[AsyncSession | None] = ContextVar(
    "request_session", default=None
)
"""Database session context variable for the current HTTP request."""
