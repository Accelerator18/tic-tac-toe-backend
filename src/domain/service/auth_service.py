from __future__ import annotations

import base64

from domain.model.sign_up_request import SignUpRequest
from domain.service.errors import UnauthorizedError, ValidationError
from domain.service.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self._user_service = user_service

    def sign_up(self, request: SignUpRequest) -> bool:
        self._user_service.create_user(request.login, request.password)
        return True

    def authorize(self, authorization_header: str | None) -> str:
        login, password = self._parse_basic_auth(authorization_header)
        user = self._user_service.validate_credentials(login, password)
        if user is None:
            raise UnauthorizedError("Неверный логин или пароль")
        return user.uuid

    def _parse_basic_auth(self, authorization_header: str | None) -> tuple[str, str]:
        if not authorization_header or not authorization_header.startswith("Basic "):
            raise UnauthorizedError("Нужен заголовок Authorization: Basic base64(login:password)")

        encoded_value = authorization_header.removeprefix("Basic ").strip()
        try:
            decoded = base64.b64decode(encoded_value).decode("utf-8")
        except Exception as exc:
            raise UnauthorizedError("Некорректный base64 в Authorization") from exc

        if ":" not in decoded:
            raise UnauthorizedError("Authorization должен содержать login:password")

        login, password = decoded.split(":", 1)
        if not login or not password:
            raise ValidationError("Логин и пароль не должны быть пустыми")
        return login, password
