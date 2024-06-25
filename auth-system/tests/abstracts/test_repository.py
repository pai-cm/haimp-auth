from typing import Optional, Tuple

import pytest

from sqlalchemy import Column, Integer, String
from dataclasses import dataclass

from src.abstracts.database.base import Base, Domain, DomainKey
from src.abstracts.database.repository import BaseRepository
from src.exceptions import AlreadyExistsException, NotFoundException


@dataclass
class SampleDomain:
    sample_id: Optional[int]
    name: str


class SampleEntity(Base[int, SampleDomain]):
    __tablename__ = 'samples'

    sample_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)

    @staticmethod
    def from_domain(domain: Domain):
        return SampleEntity(
            sample_id=domain.sample_id,
            name=domain.name
        )

    def to_domain(self):
        return SampleDomain(sample_id=self.sample_id, name=self.name)

    def update(self, domain: Domain):
        self.name = domain.name

    def primary_key(self) -> DomainKey:
        return self.sample_id


@dataclass
class Sample2Domain:
    compid0: int
    compid1: int
    name: str


class Sample2Entity(Base[Tuple[int, int], Sample2Domain]):
    __tablename__ = 'comp_samples'

    compid0 = Column(Integer, primary_key=True)
    compid1 = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    @staticmethod
    def from_domain(domain: Sample2Domain):
        return Sample2Entity(
            compid0=domain.compid0,
            compid1=domain.compid1,
            name=domain.name
        )

    def to_domain(self) -> Sample2Domain:
        return Sample2Domain(
            compid0=self.compid0,
            compid1=self.compid1,
            name=self.name
        )

    def update(self, domain: Sample2Domain):
        self.name = domain.name

    def primary_key(self) -> DomainKey:
        return [self.compid0, self.compid1]


@pytest.fixture
async def given_sample_repository(given_database):
    yield SampleRepository(given_database)


@pytest.fixture
async def given_sample2_repository(given_database):
    yield Sample2Repository(given_database)


class SampleRepository(BaseRepository):
    entity = SampleEntity


class Sample2Repository(BaseRepository):
    entity = Sample2Entity


async def test_create(given_sample_repository):
    domain = SampleDomain(None, "cm")

    await given_sample_repository.create(domain)

    assert domain.sample_id is not None


async def test_try_to_create_duplicate(given_sample_repository):
    domain = SampleDomain(None, "cm")

    await given_sample_repository.create(domain)

    with pytest.raises(AlreadyExistsException):
        await given_sample_repository.create(domain)


async def test_try_to_create_unique(given_sample_repository):
    domain0 = SampleDomain(1, "cm")
    domain1 = SampleDomain(2, "cm")

    await given_sample_repository.create(domain0)

    with pytest.raises(AlreadyExistsException):
        await given_sample_repository.create(domain1)


async def test_get_by_id(given_sample_repository):
    domain = SampleDomain(None, "cm")

    await given_sample_repository.create(domain)

    new_domain = await given_sample_repository.get_by_id(domain.sample_id)
    assert new_domain == domain


async def test_get_by_id_not_found(given_sample_repository):
    domain = SampleDomain(None, "cm")
    await given_sample_repository.create(domain)
    with pytest.raises(NotFoundException):
        await given_sample_repository.get_by_id(domain.sample_id + 1)


async def test_get_by_composite_id(given_sample2_repository):
    domain = Sample2Domain(1, 2, "cm")

    await given_sample2_repository.create(domain)

    new_domain = await given_sample2_repository.get_by_id([1, 2])
    assert new_domain == domain


async def test_find_by_id(given_sample_repository):
    domain = SampleDomain(None, "cm")
    await given_sample_repository.create(domain)
    new_domain = await given_sample_repository.find_by_id(domain.sample_id + 1)
    assert new_domain is None


async def test_update(given_sample_repository):
    domain = SampleDomain(None, "cm")
    await given_sample_repository.create(domain)
    domain.name = "new_name"
    await given_sample_repository.update(domain)
    new_domain = await given_sample_repository.find_by_id(domain.sample_id)
    assert new_domain.name == "new_name"


async def test_update_compid(given_sample2_repository):
    domain = Sample2Domain(1, 2, "cm")
    await given_sample2_repository.create(domain)
    domain.name = "new_name"
    await given_sample2_repository.update(domain)
    new_domain = await given_sample2_repository.find_by_id([1, 2])
    assert new_domain.name == "new_name"


async def test_update_not_found(given_sample_repository):
    domain = SampleDomain(None, "cm")
    await given_sample_repository.create(domain)
    domain.sample_id = 2
    with pytest.raises(NotFoundException):
        await given_sample_repository.update(domain)


async def test_update_compid_not_found(given_sample2_repository):
    domain = Sample2Domain(1, 2, "cm")
    await given_sample2_repository.create(domain)
    domain.name = "new_name"
    domain.compid0 = 2
    with pytest.raises(NotFoundException):
        await given_sample2_repository.update(domain)


async def test_save_create(given_sample_repository):
    domain0 = SampleDomain(1, "cm")
    await given_sample_repository.create(domain0)
    domain1 = SampleDomain(2, "cm2")
    await given_sample_repository.save(domain1)
    new_domain = await given_sample_repository.get_by_id(domain1.sample_id)
    assert new_domain == domain1


async def test_save_update(given_sample_repository):
    domain0 = SampleDomain(1, "cm")
    await given_sample_repository.create(domain0)
    domain0.name = "new_name"
    await given_sample_repository.save(domain0)
    new_domain = await given_sample_repository.get_by_id(domain0.sample_id)
    assert new_domain == domain0


async def test_delete(given_sample_repository):
    domain = SampleDomain(None, "cm")
    await given_sample_repository.create(domain)
    await given_sample_repository.delete(domain.sample_id)
    new_domain = await given_sample_repository.find_by_id(domain.sample_id)
    assert new_domain is None


async def test_delete_not_found(given_sample_repository):
    domain = SampleDomain(None, "cm")
    await given_sample_repository.create(domain)
    await given_sample_repository.delete(domain.sample_id)
    with pytest.raises(NotFoundException):
        await given_sample_repository.delete(domain.sample_id)


async def test_find_all(given_sample_repository):
    domain0 = SampleDomain(None, "cm")
    domain1 = SampleDomain(None, "cm2")
    await given_sample_repository.create(domain0)
    await given_sample_repository.create(domain1)
    domain_list = await given_sample_repository.find_all()
    assert domain0 in domain_list
    assert domain1 in domain_list
    assert len(domain_list) == 2


async def test_find_by(given_sample_repository):
    domain0 = SampleDomain(None, "cm")
    domain1 = SampleDomain(None, "cm2")
    await given_sample_repository.create(domain0)
    await given_sample_repository.create(domain1)
    domain_list = await given_sample_repository.find_by(name="cm")
    assert domain0 in domain_list
    assert len(domain_list) == 1
