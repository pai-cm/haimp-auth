import abc
from typing import Generic, List, Optional

from dataclasses import fields
import sqlalchemy
from sqlalchemy import select, inspect, delete, update
from sqlalchemy.orm import joinedload

from src.abstracts.database.base import SessionManager, DomainKey, Domain, Base
from src.exceptions import NotFoundException, AlreadyExistsException


def reflect_domain(src, dst):
    for field in fields(dst):
        new_value = getattr(dst, field.name)
        setattr(src, field.name, new_value)


class BaseRepository(abc.ABC, Generic[DomainKey, Domain]):
    entity: Base

    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager

    async def create(self, domain: Domain) -> None:
        async with self.session_manager.session() as session:
            await self._create(session, domain)
            await session.commit()

    async def update(self, domain: Domain) -> None:
        async with self.session_manager.session() as session:
            entity_primary_key = get_primary_key(self.entity, domain)
            try:
                entity = await self._get_by_id(session, entity_primary_key)
            except NotFoundException:
                raise NotFoundException(f"{self.entity}의 {entity_primary_key}가 발견되지 않았습니다.")
            await self._update(session, entity, domain)
            await session.commit()

    async def update_field(self, key: DomainKey, **kwargs) -> None:
        async with self.session_manager.session() as session:
            criteria = create_id_criteria(self.entity, key)
            stmt = update(self.entity).filter(*criteria).values(**kwargs)
            await session.execute(stmt)
            raise NotImplementedError("몰라")
            await session.commit()

    async def save(self, domain: Domain) -> None:
        async with self.session_manager.session() as session:
            entity_primary_key = get_primary_key(self.entity, domain)
            if entity := await self._find_by_id(session, entity_primary_key):
                await self._update(session, entity, domain)
            else:
                await self._create(session, domain)
            await session.commit()

    async def delete(self, key: DomainKey) -> None:
        async with self.session_manager.session() as session:
            criteria = create_id_criteria(self.entity, key)
            stmt = delete(self.entity).filter(*criteria)
            if (await session.execute(stmt)).rowcount == 0:
                raise NotFoundException(f"{self.entity}의 {key}가 발견되지 않았습니다.")
            await session.commit()

    async def get_by_id(self, key: DomainKey) -> Domain:
        """ key를 통해 도메인을 가져옵니다.
        (1) key가 단일키인 경우,
        ```
        await repository.get_by_id(1)
        ```

        (2) key가 복합키인 경우,
        ```
        await repository.get_by_id([1, 1])
        ```
        """
        async with self.session_manager.session() as session:
            try:
                entity = await self._get_by_id(session, key)
            except sqlalchemy.orm.exc.NoResultFound:
                raise NotFoundException(f"{self.entity}의 {key}가 발견되지 않았습니다.")
            return entity.to_domain()

    async def find_by_id(self, key: DomainKey) -> Optional[Domain]:
        async with self.session_manager.session() as session:
            if entity := await self._find_by_id(session, key):
                return entity.to_domain()

    async def find_all(self) -> List[Domain]:
        async with self.session_manager.session() as session:
            stmt = self._get_joined_select()
            entities = (await session.execute(stmt)).scalars().all()
            return [entity.to_domain() for entity in entities]

    async def find_by(self, **kwargs) -> List[Domain]:
        async with self.session_manager.session() as session:
            criteria = create_field_criteria(self.entity, kwargs)
            stmt = self._get_joined_select().filter(*criteria)

            entities = (await session.execute(stmt)).scalars().all()
            return [entity.to_domain() for entity in entities]

    def _get_joined_select(self):
        query = select(self.entity)
        for attr in inspect(self.entity).relationships:
            query = query.options(joinedload(attr.class_attribute))
        return query

    async def _get_by_id(self, session, key: DomainKey):
        criteria = create_id_criteria(self.entity, key)
        stmt = self._get_joined_select().filter(*criteria)
        return (await session.execute(stmt)).scalars().one()

    async def _find_by_id(self, session, key: DomainKey):
        criteria = create_id_criteria(self.entity, key)
        stmt = self._get_joined_select().filter(*criteria)
        return (await session.execute(stmt)).scalars().one_or_none()

    async def _create(self, session, domain: Domain) -> None:
        entity = self.entity.from_domain(domain)
        session.add(entity)
        try:
            await session.flush()
        except sqlalchemy.exc.IntegrityError:
            raise AlreadyExistsException(f"{domain} already exists")
        new_domain = entity.to_domain()
        reflect_domain(domain, new_domain)

    async def _update(self, session, entity, domain):
        entity.update(domain)
        await session.flush()
        new_domain = entity.to_domain()
        reflect_domain(domain, new_domain)


def create_id_criteria(entity: Base, key: DomainKey):
    primary_keys = inspect(entity).primary_key
    if len(primary_keys) == 1:
        return [primary_keys[0] == key]
    else:
        return [primary_key == k for primary_key, k in zip(primary_keys, key)]


def create_field_criteria(entity, kwargs):
    return [getattr(entity, key) == value for key, value in kwargs.items()]


def get_primary_key(entity: Base, domain: Domain):
    return entity.from_domain(domain).primary_key()
