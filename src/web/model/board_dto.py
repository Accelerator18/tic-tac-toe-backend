from dataclasses import dataclass


@dataclass
class BoardDto:
    cells: list[list[int]]
