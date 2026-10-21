"""Package Scrabble Enzo — Moteur Stratégique ODS8 Francophone."""

from .constants import (
    BOARD_SIZE,
    BINGO_BONUS,
    TILE_COUNTS,
    TILE_VALUES,
    BOARD_BONUS,
    tile_value,
)
from .board import Board
from .dictionary import ScrabbleDictionary
from .solver import Move, MoveGenerator
from .strategy import (
    evaluate_leave,
    evaluate_defense_penalty,
    solve_endgame_2ply,
    DuplicateGreedy,
    EnzoStrategist,
)

__all__ = [
    "BOARD_SIZE",
    "BINGO_BONUS",
    "TILE_COUNTS",
    "TILE_VALUES",
    "BOARD_BONUS",
    "tile_value",
    "Board",
    "ScrabbleDictionary",
    "Move",
    "MoveGenerator",
    "evaluate_leave",
    "evaluate_defense_penalty",
    "solve_endgame_2ply",
    "DuplicateGreedy",
    "EnzoStrategist",
]
