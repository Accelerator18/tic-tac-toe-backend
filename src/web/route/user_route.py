from flask import Blueprint, jsonify

from domain.service.errors import AppError
from domain.service.user_service import UserService
from web.auth.user_authenticator import UserAuthenticator
from web.mapper.user_web_mapper import UserWebMapper


def create_user_blueprint(
    user_service: UserService,
    user_mapper: UserWebMapper,
    authenticator: UserAuthenticator,
) -> Blueprint:
    user_blueprint = Blueprint("users", __name__, url_prefix="/users")

    @user_blueprint.get("/<user_uuid>")
    @authenticator.require_auth
    def get_user(user_uuid: str):
        try:
            user = user_service.get_by_uuid(user_uuid)
            return jsonify(user_mapper.to_json(user))
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return user_blueprint
