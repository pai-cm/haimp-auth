from datetime import datetime

from sqlalchemy import Column, String, DateTime

from src.domains import User, UserRole

from src.abstracts.database.base import Base, DomainKey


class UserEntity(Base):

    __tablename__ = "users"

    account_id = Column(String, primary_key=True)
    password = Column(String, nullable=True)

    username = Column(String, nullable=True)

    user_group = Column(String, nullable=True)
    user_role = Column(String, nullable=True)

    user_email = Column(String, nullable=True)
    user_phone = Column(String, nullable=True)

    signup_at = Column(DateTime, nullable=True,
                       default=lambda: datetime.now)

    @staticmethod
    def from_domain(domain: User, password: str):
        return UserEntity(
            account_id=domain.account_id,
            password=password,
            username=domain.name,
            user_group=domain.group,
            user_role=domain.role.value,
            user_email=domain.email,
            user_phone=domain.phone,
            signup_at=domain.signup_at,
        )

    def to_domain(self) -> User:
        return User(
            account_id=self.account_id,
            name=self.username,
            role=UserRole.from_text(self.user_role),
            group=self.user_group,
            email=self.user_email,
            phone=self.user_phone,
            signup_at=self.signup_at,
        )

    def update(self, user: User):
        self.username = user.name
        self.user_group = user.group
        self.user_role = user.role.value
        self.user_email = user.email
        self.user_phone = user.phone

    def primary_key(self) -> DomainKey:
        return self.account_id
