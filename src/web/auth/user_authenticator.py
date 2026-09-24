from __future__ import annotations

from functools import wraps

from flask import g, jsonify, request

from domain.service.auth_service import AuthService
from domain.service.errors import AppError, UnauthorizedError


class UserAuthenticator:
    def __init__(self, auth_service: AuthService):
        self._auth_service = auth_service

    def require_auth(self, view_function):
        @wraps(view_function)
        def wrapper(*args, **kwargs):
            try:
                user_uuid = self._auth_service.authorize(request.headers.get("Authorization"))
                g.user_uuid = user_uuid
                return view_function(*args, **kwargs)
            except AppError as exc:
                return jsonify({"error": str(exc)}), exc.status_code
            except Exception as exc:
                return jsonify({"error": str(exc)}), 500

        return wrapper
