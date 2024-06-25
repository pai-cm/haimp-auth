import pytest
from Crypto.PublicKey import RSA
import tempfile
import os

from src.abstracts.database.base import SessionManager
from src.settings import Settings
from src.tokens.manager import TokenManager


@pytest.fixture
def given_auth_settings(given_private_pem):
    yield Settings(
        db_type="sqlite+aiosqlite:///:memory:",
        private_key=given_private_pem
    )


@pytest.fixture
async def given_database(given_auth_settings) -> SessionManager:
    db = SessionManager(given_auth_settings)
    await db.create_database()
    yield db
    await db.drop_database()


@pytest.fixture
def given_private_key():
    return RSA.generate(1024)


@pytest.fixture
def given_public_key(given_private_key):
    return given_private_key.public_key()


@pytest.fixture
def given_private_pem(given_private_key):
    return given_private_key.export_key()


@pytest.fixture
def given_public_pem(given_public_key):
    return given_public_key.export_key()


@pytest.fixture
def given_private_pem_file(given_private_key):
    fpath = tempfile.mktemp()
    with open(fpath, "wb") as f:
        f.write(given_private_key.export_key())
    yield fpath
    os.remove(fpath)


@pytest.fixture
def given_public_pem_file(given_public_key):
    fpath = tempfile.mktemp()
    with open(fpath, "wb") as f:
        f.write(given_public_key.export_key())
    yield fpath
    os.remove(fpath)


@pytest.fixture
def given_token_manager(given_auth_settings) -> TokenManager:
    return TokenManager(given_auth_settings)
