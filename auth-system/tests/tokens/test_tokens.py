from datetime import datetime

import pytest
import jwt

from src.domain import TokenType, User, UserRole
from src.exceptions import ExpiredTokenException
from src.tokens.manager import create_jwt_token


@pytest.fixture
def given_user():
    return User(
        account_id="paicm",
        name="김채민",
        role=UserRole.ADMIN,
        group="paip",
        email="pai-cm@publicai.co.kr",
        phone="010-1234-1234",
        signup_at=datetime.now()
    )


def test_create_jwt_token_access(given_private_pem, given_public_pem):
    # given
    given_payload = {
        "account_id": "paicm",
        "user_role": "admin",
        "user_group": "paip"
    }

    # when
    access_token = create_jwt_token(given_payload, TokenType.ACCESS, given_private_pem, 10)

    payload = jwt.decode(access_token, given_public_pem, algorithms=['RS256'])

    # then
    assert payload['type'] == "access"
    assert payload['account_id'] == "paicm"


def test_create_jwt_token_expired_case(given_private_pem, given_public_pem):
    # given
    given_payload = {
        "account_id": "paicm",
        "user_role": "admin",
        "user_group": "paip"
    }

    # when
    access_token = create_jwt_token(given_payload, TokenType.ACCESS, given_private_pem, -10)

    with pytest.raises(jwt.exceptions.ExpiredSignatureError):
        jwt.decode(access_token, given_public_pem, algorithms=['RS256'])


def test_create_jwt_token_refresh(given_private_pem, given_public_pem):
    # given
    given_payload = {
    }

    # when
    refresh_token = create_jwt_token(given_payload, TokenType.REFRESH, given_private_pem, 10)

    payload = jwt.decode(refresh_token, given_public_pem, algorithms=['RS256'])

    # then
    assert payload['type'] == "refresh"


def test_generate_token(given_user, given_public_pem, given_token_manager):
    # user
    token = given_token_manager.generate_token(given_user)
    output = jwt.decode(token.access, given_public_pem, algorithms=['RS256'])

    assert given_user.to_jwt_payload()["account_id"] == output["account_id"]


def test_verify_refresh_token(given_user, given_token_manager):
    # user
    token = given_token_manager.generate_token(given_user)
    user_name = given_token_manager.verify_refresh_token(token.refresh)

    assert user_name == given_user.account_id


def test_verify_refresh_token_with_expired(given_token_manager, given_private_pem):
    # given
    given_payload = {
        "account_id": "paicm"
    }

    # when
    refresh_token = create_jwt_token(given_payload, TokenType.REFRESH, given_private_pem, -10)

    with pytest.raises(ExpiredTokenException):
        given_token_manager.verify_refresh_token(refresh_token)
