from src.domain import User, LoginRequest, Token
from src.exceptions import DBIntegrityException, AlreadyExistsException
from src.tokens.manager import TokenManager
from src.users.repository import UserRepository
from src.common import validate_active_user


class LoginManager:
    """로그인 매니저"""

    def __init__(self, user_repository: UserRepository, token_manager: TokenManager):
        """LoginManager 초기화 메서드

        Args:
            user_repository: UserRepository
            token_manager: TokenManager
        """
        self.user_repository = user_repository
        self.token_manager = token_manager

    async def sign_up(self, user: User, password: str) -> Token:
        """사용자의 정보와 비밀번호로 사용자의 정보 저장을 요청합니다.
        사용자의 정보로 토큰 생성 요청 후 토큰을 반환합니다.

        Args:
            user: 사용자 정보를 포함하는 도메인
            password: 사용자 비밀번호

        Returns:
            Token: access token, refresh token을 포함하는 도메인

        Raises:
            AlreadyExistException: 아이디가 DB에 이미 존재할 때 발생합니다.
        """
        try:
            await self.user_repository.create_user(user, password)
            return self.token_manager.generate_token(user)
        except DBIntegrityException:
            raise AlreadyExistsException("이미 존재하는 유저 아이디입니다.")

    async def login(self, login_request: LoginRequest) -> Token:
        """사용자의 login 정보로 사용자의 정보를 요청하고, 해당 정보로 토큰을 반환합니다.

        Args:
            login_request: 로그인 시 필요한 정보를 포함하는 도메인

        Returns:
            Token: access token, refresh token을 포함하는 도메인
        """
        user = await self.user_repository.find_by(account_id=login_request.account_id, password=login_request.password)
        validate_active_user(user)
        return self.token_manager.generate_token(user=user)

    async def refresh(self, refresh_token: str) -> Token:
        """요청받은 refresh 토큰을 검증하고, 새로운 토큰을 반환합니다.

        Args:
            refresh_token: refresh token

        Returns:
            Token: access token, refresh token을 포함하는 도메인
        """
        account_id = self.token_manager.verify_refresh_token(refresh_token)
        user = await self.user_repository.get_by_id(account_id)
        return self.token_manager.generate_token(user)
