from __future__ import annotations

from uuid import UUID, uuid4

from domain.model.board import Board, X_MARK, O_MARK
from domain.model.game import Game, GameMode, GameStatus
from domain.service.errors import ForbiddenError, NotFoundError, ValidationError
from domain.service.game_logic_service import GameLogicService
from datasource.repository.game_repository import GameRepository


class GameService:
    def __init__(self, repository: GameRepository, logic: GameLogicService):
        self._repository = repository
        self._logic = logic

    def create_game(self, creator_uuid: str, mode: GameMode) -> Game:
        game_uuid = str(uuid4())
        if mode == GameMode.COMPUTER:
            game = Game(
                uuid=game_uuid,
                board=Board.empty(),
                mode=mode,
                status=GameStatus.TURN,
                player_x_uuid=creator_uuid,
                player_o_uuid=None,
                current_turn_uuid=creator_uuid,
                winner_uuid=None,
            )
        else:
            game = Game(
                uuid=game_uuid,
                board=Board.empty(),
                mode=mode,
                status=GameStatus.WAITING_PLAYERS,
                player_x_uuid=creator_uuid,
                player_o_uuid=None,
                current_turn_uuid=None,
                winner_uuid=None,
            )
        return self._repository.save(game)

    def get_game(self, game_uuid: str) -> Game:
        self._validate_uuid(game_uuid)
        game = self._repository.get_by_uuid(game_uuid)
        if game is None:
            raise NotFoundError("Игра не найдена")
        return game

    def get_available_games(self, current_user_uuid: str) -> list[Game]:
        return self._repository.get_available_games(current_user_uuid)

    def get_my_games(self, current_user_uuid: str) -> list[Game]:
        return self._repository.get_games_for_user(current_user_uuid)

    def join_game(self, game_uuid: str, user_uuid: str) -> Game:
        game = self.get_game(game_uuid)
        if game.mode != GameMode.USER:
            raise ValidationError("К игре с компьютером нельзя присоединиться вторым игроком")
        if game.status != GameStatus.WAITING_PLAYERS:
            raise ValidationError("К этой игре уже нельзя присоединиться")
        if game.player_x_uuid == user_uuid:
            raise ValidationError("Нельзя присоединиться к своей игре вторым игроком")

        game.player_o_uuid = user_uuid
        game.status = GameStatus.TURN
        game.current_turn_uuid = game.player_x_uuid
        return self._repository.save(game)

    def update_game(self, game_uuid: str, user_uuid: str, new_board: Board) -> Game:
        game = self.get_game(game_uuid)

        if game.status == GameStatus.WAITING_PLAYERS:
            raise ValidationError("Игра ожидает второго игрока")
        if game.is_finished():
            raise ValidationError("Игра уже завершена")
        if not game.has_player(user_uuid):
            raise ForbiddenError("Пользователь не является участником этой игры")
        if game.current_turn_uuid != user_uuid:
            raise ValidationError("Сейчас ход другого игрока")

        user_mark = game.get_user_mark(user_uuid)
        if user_mark is None:
            raise ForbiddenError("Не удалось определить знак игрока")

        self._logic.validate_one_new_move(game.board, new_board, user_mark)
        game.board = new_board
        self._update_state_after_player_move(game, user_mark, user_uuid)

        if game.is_finished():
            return self._repository.save(game)

        if game.mode == GameMode.COMPUTER:
            game.board = self._logic.make_computer_move(game.board)
            self._update_state_after_player_move(game, O_MARK, None)
            if not game.is_finished():
                game.current_turn_uuid = game.player_x_uuid
        else:
            game.current_turn_uuid = game.player_o_uuid if user_uuid == game.player_x_uuid else game.player_x_uuid

        return self._repository.save(game)

    def _update_state_after_player_move(self, game: Game, mark: int, user_uuid: str | None) -> None:
        winner_mark = self._logic.check_winner(game.board)
        if winner_mark != 0:
            game.status = GameStatus.WIN
            if winner_mark == X_MARK:
                game.winner_uuid = game.player_x_uuid
            elif winner_mark == O_MARK:
                game.winner_uuid = game.player_o_uuid if game.mode == GameMode.USER else "COMPUTER"
            game.current_turn_uuid = None
            return

        if self._logic.is_draw(game.board):
            game.status = GameStatus.DRAW
            game.current_turn_uuid = None
            game.winner_uuid = None
            return

        game.status = GameStatus.TURN

    def _validate_uuid(self, value: str) -> None:
        try:
            UUID(value)
        except ValueError as exc:
            raise ValidationError("Некорректный UUID игры") from exc
