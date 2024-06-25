from src.abstracts.database.repository import BaseRepository
from src.users.models import UserEntity


class UserRepository(BaseRepository):
    entity = UserEntity
