import asyncio
from contextlib import AbstractContextManager, asynccontextmanager
from typing import Callable, TypeVar, Generic
import logging

import sqlalchemy.exc
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

from src.exceptions import DatabaseException, NotFoundException, DBIntegrityException
from src.settings import Settings

logger = logging.getLogger(__name__)

DomainKey = TypeVar("DomainKey")
Domain = TypeVar("Domain")


class Base(AsyncAttrs, DeclarativeBase, Generic[DomainKey, Domain]):
    __abstract__ = True

    @staticmethod
    def from_domain(domain: Domain):
        raise NotImplementedError("from_domain method is not implemented")

    def to_domain(self) -> Domain:
        raise NotImplementedError("to_domain method is not implemented")

    def update(self, domain: Domain):
        raise NotImplementedError("update method is not implemented")

    def primary_key(self) -> DomainKey:
        raise NotImplementedError("primary_key method is not implemented")


class SessionManager:
    """비동기 데이터베이스 클래스"""

    def __init__(self, settings: Settings):
        if settings.db_type.startswith('sqlite'):
            self._engine = create_async_engine(settings.db_type)
        elif settings.db_type.startswith("postgresql"):
            url = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_host}/{settings.db_name}"
            self._engine = create_async_engine(url)
        else:
            raise DatabaseException(f"지원하지 않는 database type입니다. {settings.db_type}")

        self._session_factory = async_scoped_session(
            async_sessionmaker(
                autocommit=False,
                bind=self._engine,
            ),
            scopefunc=asyncio.current_task,
        )

    async def create_database(self) -> None:
        if self._engine.url.drivername != "sqlite+aiosqlite":
            raise ValueError("create_database should be used for test mode only.")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_database(self) -> None:
        if self._engine.url.drivername != "sqlite+aiosqlite":
            raise ValueError("drop_database should be used for test mode only.")
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            yield session
        except sqlalchemy.exc.NoResultFound:
            await session.rollback()
            raise NotFoundException("데이터를 못 발견 했어요")
        except sqlalchemy.exc.IntegrityError:
            await session.rollback()
            raise DBIntegrityException("데이터를 못 발견 했어요")
        except DatabaseException as e:
            await session.rollback()
            raise e
        except Exception as e:
            logger.exception("Session rollback because of exception")
            await session.rollback()
            raise DatabaseException(f"{e}")
        finally:
            await session.close()
            await self._session_factory.remove()

    async def connect(self):
        return await self._engine.connect()
