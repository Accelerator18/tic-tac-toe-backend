from __future__ import annotations

from domain.model.board import Board, EMPTY, X_MARK, O_MARK
from domain.service.errors import ValidationError


class GameLogicService:


    def check_winner(self, board: Board) -> int:
        board.validate()
        cells = board.cells
        lines: list[list[int]] = []

        # строки
        lines.extend(cells)

        # столбцы
        for column in range(3):
            lines.append([cells[0][column], cells[1][column], cells[2][column]])

        # диагонали
        lines.append([cells[0][0], cells[1][1], cells[2][2]])
        lines.append([cells[0][2], cells[1][1], cells[2][0]])

        for line in lines:
            if line[0] != EMPTY and line[0] == line[1] == line[2]:
                return line[0]
        return EMPTY

    def is_draw(self, board: Board) -> bool:
        return self.check_winner(board) == EMPTY and len(board.empty_cells()) == 0

    def validate_one_new_move(self, old_board: Board, new_board: Board, mark: int) -> None:
        old_board.validate()
        new_board.validate()

        changed_cells = []
        for row in range(3):
            for column in range(3):
                old_value = old_board.cells[row][column]
                new_value = new_board.cells[row][column]

                if old_value != EMPTY and old_value != new_value:
                    raise ValidationError("Нельзя изменять уже сделанные ходы")

                if old_value == EMPTY and new_value != EMPTY:
                    changed_cells.append((row, column, new_value))

        if len(changed_cells) != 1:
            raise ValidationError("За один запрос можно сделать ровно один новый ход")

        _, _, value = changed_cells[0]
        if value != mark:
            raise ValidationError("Игрок поставил не свой знак")

    def make_computer_move(self, board: Board) -> Board:
        board.validate()

        if self.check_winner(board) != EMPTY or self.is_draw(board):
            return board.copy()

        best_score = float("-inf")
        best_move: tuple[int, int] | None = None

        for row, column in board.empty_cells():
            candidate = board.copy()
            candidate.cells[row][column] = O_MARK
            score = self._minimax(candidate, is_computer_turn=False, depth=1)
            if score > best_score:
                best_score = score
                best_move = (row, column)

        result = board.copy()
        if best_move is not None:
            result.cells[best_move[0]][best_move[1]] = O_MARK
        return result

    def _minimax(self, board: Board, is_computer_turn: bool, depth: int) -> int:
        winner = self.check_winner(board)
        if winner == O_MARK:
            return 10 - depth
        if winner == X_MARK:
            return depth - 10
        if self.is_draw(board):
            return 0

        if is_computer_turn:
            best_score = float("-inf")
            for row, column in board.empty_cells():
                candidate = board.copy()
                candidate.cells[row][column] = O_MARK
                score = self._minimax(candidate, is_computer_turn=False, depth=depth + 1)
                best_score = max(best_score, score)
            return int(best_score)

        best_score = float("inf")
        for row, column in board.empty_cells():
            candidate = board.copy()
            candidate.cells[row][column] = X_MARK
            score = self._minimax(candidate, is_computer_turn=True, depth=depth + 1)
            best_score = min(best_score, score)
        return int(best_score)
