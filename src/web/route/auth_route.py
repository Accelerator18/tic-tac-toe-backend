from flask import Blueprint, jsonify, request

from domain.model.sign_up_request import SignUpRequest
from domain.service.auth_service import AuthService
from domain.service.errors import AppError


def create_auth_blueprint(auth_service: AuthService) -> Blueprint:
    auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

    @auth_blueprint.post("/signup")
    def sign_up():
        try:
            data = request.get_json(silent=True) or {}
            sign_up_request = SignUpRequest(
                login=str(data.get("login", "")),
                password=str(data.get("password", "")),
            )
            success = auth_service.sign_up(sign_up_request)
            return jsonify({"success": success}), 201
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @auth_blueprint.post("/login")
    def login():
        try:
            user_uuid = auth_service.authorize(request.headers.get("Authorization"))
            return jsonify({"uuid": user_uuid})
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return auth_blueprint
