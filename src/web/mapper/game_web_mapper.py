from domain.model.game import Game, GameMode
from web.mapper.board_web_mapper import BoardWebMapper


class GameWebMapper:
    def __init__(self, board_mapper: BoardWebMapper):
        self._board_mapper = board_mapper

    def to_json(self, game: Game) -> dict:
        return {
            "uuid": game.uuid,
            "board": self._board_mapper.to_json(game.board),
            "mode": game.mode.value,
            "status": game.status.value,
            "currentTurnUserUuid": game.current_turn_uuid,
            "winnerUserUuid": game.winner_uuid,
            "players": {
                "X": game.player_x_uuid,
                "O": game.player_o_uuid if game.mode == GameMode.USER else "COMPUTER",
            },
            "marks": {
                "empty": 0,
                "X": 1,
                "O": 2,
            },
        }

    def list_to_json(self, games: list[Game]) -> list[dict]:
        return [self.to_json(game) for game in games]
