class PaipAuthException(Exception):
    message: str

    def __init__(self, message: str):
        self.message = message


class DatabaseException(PaipAuthException):
    """데이터 베이스에서 발생한 Exception"""


class NotFoundException(DatabaseException):
    """데이터를 찾지 못했을 때"""


class AlreadyExistsException(DatabaseException):
    """이미 데이터가 존재할 때"""


class UnAuthorizedException(DatabaseException):
    """인증되지 않은 사용자일 때"""


class DBIntegrityException(DatabaseException):
    """무결성 에러"""


class InvalidTokenException(PaipAuthException):
    """잘못된 토큰일 때"""


class ExpiredTokenException(InvalidTokenException):
    """만료된 토큰일 때"""
