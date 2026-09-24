from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from domain.model.board import Board, X_MARK, O_MARK


class GameMode(StrEnum):
    COMPUTER = "COMPUTER"
    USER = "USER"


class GameStatus(StrEnum):
    WAITING_PLAYERS = "WAITING_PLAYERS"
    TURN = "TURN"
    DRAW = "DRAW"
    WIN = "WIN"


@dataclass
class Game:
    uuid: str
    board: Board
    mode: GameMode
    status: GameStatus
    player_x_uuid: str
    player_o_uuid: str | None = None
    current_turn_uuid: str | None = None
    winner_uuid: str | None = None

    def get_user_mark(self, user_uuid: str) -> int | None:
        if user_uuid == self.player_x_uuid:
            return X_MARK
        if user_uuid == self.player_o_uuid:
            return O_MARK
        return None

    def is_finished(self) -> bool:
        return self.status in (GameStatus.DRAW, GameStatus.WIN)

    def has_player(self, user_uuid: str) -> bool:
        return user_uuid in (self.player_x_uuid, self.player_o_uuid)
