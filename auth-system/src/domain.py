from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional

from src.exceptions import InvalidTokenException


class UserRole(Enum):
    PENDING = 'PENDING'
    MEMBER = 'MEMBER'
    VIP = 'VIP'
    DATA_MANAGEMENT = 'DATA_MANAGEMENT'
    ADMIN = 'ADMIN'
    WITHDRAWAL = 'WITHDRAWAL'
    UNKNOWN = 'UNKNOWN'

    AUTH = 'AUTH'
    SIDECAR = 'SIDECAR'

    @staticmethod
    def from_text(text: str):
        for role in UserRole:
            if role.value == text.upper():
                return role
        return UserRole.UNKNOWN

    @property
    def is_admin(self):
        return self == UserRole.ADMIN

    @property
    def display(self):
        if self == UserRole.PENDING:
            return "승인 대기"
        elif self == UserRole.MEMBER:
            return "일반 사용자"
        elif self == UserRole.VIP:
            return "고급 사용자"
        elif self == UserRole.DATA_MANAGEMENT:
            return "데이터 관리자"
        elif self == UserRole.ADMIN:
            return "플랫폼 관리자"
        elif self == UserRole.WITHDRAWAL:
            return "탈퇴 회원"
        else:
            return "알수 없음"


@dataclass
class LoginRequest:
    """ 로그인에 필요한 필수 정보"""
    account_id: str
    password: Optional[str]


@dataclass
class UserAuth:
    """ 유저의 인증 정보
    == JWT payload에 들어가는 정보이기도 함
    """
    account_id: str
    role: UserRole
    group: str

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "user_role": self.role.value,
            "user_group": self.group,
        }


@dataclass
class User:
    """유저 정보"""
    account_id: str
    name: str
    role: UserRole
    group: str
    email: str
    phone: str
    signup_at: datetime

    @staticmethod
    def new(account_id: str, name: str, email: str, phone: str):
        return User(
            account_id=account_id,
            name=name,
            role=UserRole.PENDING,
            group="default",
            email=email,
            phone=phone,
            signup_at=datetime.now()
        )

    def to_user_auth(self):
        return UserAuth(
            account_id=self.account_id,
            role=self.role,
            group=self.group
        )

    def to_jwt_payload(self):
        """jwt payload에 담을 정보로 변경"""
        return self.to_user_auth().to_dict()


@dataclass
class Token:
    """JWT Token 객체"""
    access: str
    refresh: str


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"

    @staticmethod
    def from_text(text: str) -> 'TokenType':
        for token_type in TokenType:
            if token_type.value.lower().strip() == text.lower().strip():
                return token_type
        raise InvalidTokenException("유효하지 않은 토큰 타입입니다.")
