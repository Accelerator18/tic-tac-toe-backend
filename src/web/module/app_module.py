from __future__ import annotations

import os

from flask import Flask, jsonify

from datasource.database import db
# Эти импорты нужны, чтобы SQLAlchemy увидел модели перед create_all().
from datasource.model.game_entity import GameEntity  # noqa: F401
from datasource.model.user_entity import UserEntity  # noqa: F401
from di.container import Container
from domain.service.errors import AppError
from web.route.auth_route import create_auth_blueprint
from web.route.game_route import create_game_blueprint
from web.route.page_route import create_page_blueprint
from web.route.user_route import create_user_blueprint


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "For this project PostgreSQL is required, for example: "
            "export DATABASE_URL='postgresql+psycopg2://postgres:postgres@localhost:5432/tic_tac_toe'"
        )
    if not database_url.startswith(("postgresql://", "postgresql+psycopg2://")):
        raise RuntimeError("Only PostgreSQL connection URL is allowed for Backend 04.")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    container = Container()

    app.register_blueprint(create_page_blueprint())
    app.register_blueprint(create_auth_blueprint(container.auth_service))
    app.register_blueprint(
        create_game_blueprint(
            container.game_service,
            container.board_web_mapper,
            container.game_web_mapper,
            container.authenticator,
        )
    )
    app.register_blueprint(
        create_user_blueprint(
            container.user_service,
            container.user_web_mapper,
            container.authenticator,
        )
    )

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"})

    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({"error": str(error)}), error.status_code

    return app
