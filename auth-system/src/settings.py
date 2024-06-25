from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Auth를 위한 환경 변수 목록들"""

    db_type: str = Field(
        description="DB 유형",
        default='sqlite+aiosqlite:///:memory:'
    )

    db_host: str = Field(
        description="db host",
        default="paip-database"
    )

    db_name: str = Field(
        default="haimp-auth",
        description="디비 스키마 이름"
    )

    db_user: str = Field(
        default="admin",
        description="디비 유저 이름"
    )

    db_password: str = Field(
        default="admin123",
        description="디비 패스워드 이름"
    )

    private_key: bytes = Field(
        description='Private Pem Contents'
    )

    access_token_lifetime: int = Field(
        description="Access Token 수명(단위 초)",
        default=86400,  # 하루
    )

    refresh_token_lifetime: int = Field(
        description="Refresh Token 수명(단위 초)",
        default=2592000,  # 한달
    )
