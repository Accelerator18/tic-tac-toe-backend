from domain.model.board import Board
from web.model.board_dto import BoardDto


class BoardWebMapper:
    def from_json(self, data: dict) -> Board:
        if not isinstance(data, dict) or "board" not in data:
            raise ValueError("В JSON должно быть поле board")
        board = Board(data["board"])
        board.validate()
        return board

    def to_json(self, board: Board) -> list[list[int]]:
        return board.cells
