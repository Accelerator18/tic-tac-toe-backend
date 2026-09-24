from flask import Blueprint, g, jsonify, request

from domain.model.game import GameMode
from domain.service.errors import AppError, ValidationError
from domain.service.game_service import GameService
from web.auth.user_authenticator import UserAuthenticator
from web.mapper.board_web_mapper import BoardWebMapper
from web.mapper.game_web_mapper import GameWebMapper


def create_game_blueprint(
    game_service: GameService,
    board_mapper: BoardWebMapper,
    game_mapper: GameWebMapper,
    authenticator: UserAuthenticator,
) -> Blueprint:
    game_blueprint = Blueprint("games", __name__)

    @game_blueprint.post("/games")
    @authenticator.require_auth
    def create_game():
        try:
            data = request.get_json(silent=True) or {}
            mode_value = str(data.get("mode") or data.get("opponent") or "computer").upper()
            if mode_value in ("COMPUTER", "AI", "BOT"):
                mode = GameMode.COMPUTER
            elif mode_value in ("USER", "PLAYER", "HUMAN"):
                mode = GameMode.USER
            else:
                raise ValidationError("mode должен быть COMPUTER или USER")

            game = game_service.create_game(g.user_uuid, mode)
            return jsonify(game_mapper.to_json(game)), 201
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @game_blueprint.get("/games/available")
    @authenticator.require_auth
    def get_available_games():
        try:
            games = game_service.get_available_games(g.user_uuid)
            return jsonify({"games": game_mapper.list_to_json(games)})
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @game_blueprint.get("/games/my")
    @authenticator.require_auth
    def get_my_games():
        try:
            games = game_service.get_my_games(g.user_uuid)
            return jsonify({"games": game_mapper.list_to_json(games)})
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @game_blueprint.post("/games/<game_uuid>/join")
    @authenticator.require_auth
    def join_game(game_uuid: str):
        try:
            game = game_service.join_game(game_uuid, g.user_uuid)
            return jsonify(game_mapper.to_json(game))
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @game_blueprint.get("/games/<game_uuid>")
    @authenticator.require_auth
    def get_game(game_uuid: str):
        try:
            game = game_service.get_game(game_uuid)
            if not game.has_player(g.user_uuid):
                return jsonify({"error": "Пользователь не является участником этой игры"}), 403
            return jsonify(game_mapper.to_json(game))
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    @game_blueprint.post("/games/<game_uuid>")
    @authenticator.require_auth
    def update_game(game_uuid: str):
        try:
            board = board_mapper.from_json(request.get_json(silent=True) or {})
            game = game_service.update_game(game_uuid, g.user_uuid, board)
            return jsonify(game_mapper.to_json(game))
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400
        except AppError as exc:
            return jsonify({"error": str(exc)}), exc.status_code
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500


    @game_blueprint.post("/game/<game_uuid>")
    @authenticator.require_auth
    def update_game_old_route(game_uuid: str):
        return update_game(game_uuid)

    return game_blueprint
