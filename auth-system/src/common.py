from src.domain import User, UserRole
from src.exceptions import UnAuthorizedException


def validate_active_user(user: User):
    """활동 중인 사용자 검증 함수

    Args:
        user: 사용자 정보 Domain 객체

    Raises:
        UnAuthorizedException: 사용자 권한이 WITHDRAWAL 경우 발생합니다.
    """
    if user.role == UserRole.WITHDRAWAL:
        raise UnAuthorizedException("해당 계정은 탈퇴한 계정입니다.")
