"""Représentation de la grille 15x15 de Scrabble et gestion des coordonnées FISF."""

from __future__ import annotations
import copy
from typing import Optional, Tuple, Dict, List
from .constants import BOARD_SIZE, TILE_COUNTS, BOARD_BONUS

class Board:
    """Grille de Scrabble 15x15 avec gestion de l'état, de la notation FISF et du sac restant."""

    def __init__(self, grid: Optional[List[List[Optional[str]]]] = None):
        if grid is not None:
            self.grid = [list(row) for row in grid]
        else:
            self.grid = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    def is_empty(self) -> bool:
        """Vérifie si aucune lettre n'a encore été posée sur le plateau."""
        return all(self.grid[r][c] is None for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    def get_tile(self, r: int, c: int) -> Optional[str]:
        """Retourne la lettre présente en (r, c) ou None."""
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return self.grid[r][c]
        return None

    def set_tile(self, r: int, c: int, ch: Optional[str]) -> None:
        """Place ou efface un jeton en (r, c)."""
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            self.grid[r][c] = ch

    def copy(self) -> Board:
        """Retourne une copie profonde de la grille."""
        return Board([row[:] for row in self.grid])

    @staticmethod
    def format_coord_fisf(row: int, col: int, horizontal: bool) -> str:
        """Formate les coordonnées selon la notation officielle FISF (ex. H4 ou 4H)."""
        row_letter = chr(ord('A') + row)
        col_number = col + 1
        if horizontal:
            return f"{row_letter}{col_number}"
        return f"{col_number}{row_letter}"

    @staticmethod
    def parse_coord_fisf(ref: str) -> Tuple[int, int, bool]:
        """Convertit une référence FISF (ex. 'H4' ou '4H') en (row, col, horizontal)."""
        ref = ref.strip().upper()
        if not ref:
            raise ValueError("Référence FISF vide")

        if ref[0].isalpha():
            # Horizontal (ex. H4)
            row = ord(ref[0]) - ord('A')
            col = int(ref[1:]) - 1
            return row, col, True
        else:
            # Vertical (ex. 4H, 14H)
            col = int(ref[:-1]) - 1
            row = ord(ref[-1]) - ord('A')
            return row, col, False

    def remaining_tiles(self, rack: str = "") -> Dict[str, int]:
        """Calcule les jetons restants dans le sac après déduction du plateau et du chevalet."""
        counts = dict(TILE_COUNTS)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                tile = self.grid[r][c]
                if tile is not None:
                    if tile.islower():
                        key = '?'
                    else:
                        key = tile.upper()
                    counts[key] = max(0, counts.get(key, 0) - 1)

        for ch in rack:
            if ch.islower() or ch == '?':
                key = '?'
            else:
                key = ch.upper()
            counts[key] = max(0, counts.get(key, 0) - 1)

        return counts

    def total_remaining_tiles(self, rack: str = "") -> int:
        """Nombre total de jetons encore dans le sac."""
        return sum(self.remaining_tiles(rack).values())

    def to_ascii(self) -> str:
        """Affiche la grille au format texte avec numéros de lignes et colonnes."""
        header = "    " + " ".join(f"{c+1:2}" for c in range(BOARD_SIZE))
        lines = [header]
        for r in range(BOARD_SIZE):
            row_letter = chr(ord('A') + r)
            row_str = []
            for c in range(BOARD_SIZE):
                t = self.grid[r][c]
                if t is not None:
                    row_str.append(f" {t}")
                else:
                    b = BOARD_BONUS[r][c]
                    if b:
                        row_str.append(b.rjust(2))
                    else:
                        row_str.append(" .")
            lines.append(f"{row_letter:2}  " + " ".join(row_str))
        return "\n".join(lines)

    def to_dict(self) -> List[List[Optional[str]]]:
        """Convertit la grille en matrice sérialisable JSON."""
        return [row[:] for row in self.grid]

    @classmethod
    def from_dict(cls, data: List[List[Optional[str]]]) -> Board:
        """Reconstitue un plateau depuis une matrice JSON."""
        return cls(data)
