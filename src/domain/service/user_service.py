from __future__ import annotations

from uuid import uuid4

from werkzeug.security import check_password_hash, generate_password_hash

from domain.model.user import User
from domain.service.errors import NotFoundError, ValidationError
from datasource.repository.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository):
        self._repository = repository

    def create_user(self, login: str, password: str) -> User:
        login = login.strip()
        if len(login) < 3:
            raise ValidationError("Логин должен содержать минимум 3 символа")
        if len(password) < 4:
            raise ValidationError("Пароль должен содержать минимум 4 символа")
        if self._repository.get_by_login(login) is not None:
            raise ValidationError("Пользователь с таким логином уже существует")

        user = User(
            uuid=str(uuid4()),
            login=login,
            password_hash=generate_password_hash(password),
        )
        return self._repository.save(user)

    def get_by_uuid(self, user_uuid: str) -> User:
        user = self._repository.get_by_uuid(user_uuid)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    def validate_credentials(self, login: str, password: str) -> User | None:
        user = self._repository.get_by_login(login)
        if user is None:
            return None
        if not check_password_hash(user.password_hash, password):
            return None
        return user
