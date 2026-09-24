from __future__ import annotations

from dataclasses import dataclass


EMPTY = 0
X_MARK = 1
O_MARK = 2
BOARD_SIZE = 3


@dataclass
class Board:
    cells: list[list[int]]

    @staticmethod
    def empty() -> "Board":
        return Board([[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)])

    def copy(self) -> "Board":
        return Board([row[:] for row in self.cells])

    def validate(self) -> None:
        if not isinstance(self.cells, list) or len(self.cells) != BOARD_SIZE:
            raise ValueError("Игровое поле должно быть матрицей 3x3")

        for row in self.cells:
            if not isinstance(row, list) or len(row) != BOARD_SIZE:
                raise ValueError("Каждая строка игрового поля должна содержать 3 клетки")
            for value in row:
                if value not in (EMPTY, X_MARK, O_MARK):
                    raise ValueError("Клетки поля могут содержать только 0, 1 или 2")

    def empty_cells(self) -> list[tuple[int, int]]:
        self.validate()
        result: list[tuple[int, int]] = []
        for row_index in range(BOARD_SIZE):
            for column_index in range(BOARD_SIZE):
                if self.cells[row_index][column_index] == EMPTY:
                    result.append((row_index, column_index))
        return result

    def count(self, value: int) -> int:
        return sum(row.count(value) for row in self.cells)

    def get_cell(self, row: int, column: int) -> int:
        return self.cells[row][column]

    def set_cell(self, row: int, column: int, value: int) -> None:
        if self.cells[row][column] != EMPTY:
            raise ValueError("Нельзя ходить в занятую клетку")
        self.cells[row][column] = value
