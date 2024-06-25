from typing import Dict

import jwt

from src.tokens.auth import private_pem2public_pem
from src.domain import User, Token, TokenType

from datetime import datetime

from src.exceptions import ExpiredTokenException, InvalidTokenException
from src.settings import Settings


class TokenManager:
    """토큰 관리 매니저"""

    def __init__(self, settings: Settings):
        """
        TokenManager 초기화 메서드

        Args:
            settings: AuthSettings
        """
        self.private_key = settings.private_key
        self.access_token_lifetime = settings.access_token_lifetime
        self.refresh_token_lifetime = settings.refresh_token_lifetime

    def generate_token(self, user: User) -> Token:
        """jwt token을 생성하고, access token, refresh token을 포함하는 도메인을 반환합니다.

        Args:
            user: 사용자 정보를 포함하는 도메인

        Returns:
            Token: access token, refresh token을 포함하는 도메인
        """
        # access token 만들기
        access = create_jwt_token(
            user.to_jwt_payload(),
            TokenType.ACCESS,
            self.private_key,
            self.access_token_lifetime
        )

        # refresh token 만들기
        refresh = create_jwt_token(
            {"account_id": user.account_id}, TokenType.REFRESH, self.private_key, self.refresh_token_lifetime
        )

        return Token(access=access, refresh=refresh)

    def verify_refresh_token(self, refresh_token: str) -> str:
        """요청 받은 refresh token 이 유효한지 검증합니다.

        Args:
            refresh_token: refresh token

        Returns:
            str: refresh token을 decode하여 추출한 사용자의 계정

        Raises:
            ExpiredTokenException: refresh token이 만료되었을 경우 발생합니다.
        """
        public_key = private_pem2public_pem(self.private_key)
        try:
            output = jwt.decode(refresh_token, public_key, algorithms=['RS256'])
            return output["account_id"]
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenException("리프레시 토큰이 만료되었습니다.")

    def verify_access_token(self, access_token: str):
        """요청 받은 access token 이 유효한지 검증합니다.

        Args:
            access_token: access token

        Returns:
            dict: access token을 decode하여 추출한 payload

        Raises:
            ExpiredTokenException: access token이 만료되었을 경우 발생합니다.
            InvalidTokenException: access token의 검증이 실패했을 경우 발생합니다.
        """
        try:
            public_key = private_pem2public_pem(self.private_key)
            payload = jwt.decode(access_token, public_key, algorithms=['RS256'])
            return payload

        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenException("만료된 토큰 입니다")

        except jwt.exceptions.InvalidSignatureError:
            raise InvalidTokenException("검증 실패 토큰 입니다")


def create_jwt_token(
        payload: Dict,
        token_type: TokenType,
        private_key: bytes,
        lifetime: int
) -> str:
    """JWT 토큰을 생성합니다.

    Args:
        payload: 토큰에 포함할 정보 payload
        token_type: 토큰 유형 ex. access, refresh
        private_key: private key
        lifetime: 토큰 수명

    Returns:
        str: jwt token
    """
    update_payload = {
        **payload,
        "type": token_type.value,
        "exp": datetime.now().timestamp() + lifetime,
        "iat": datetime.now().timestamp(),
    }

    jwt_token = jwt.encode(update_payload, private_key, algorithm='RS256')

    return jwt_token
