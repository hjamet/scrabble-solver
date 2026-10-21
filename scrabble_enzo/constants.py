"""Constantes officielles du Scrabble francophone (ODS8)."""

BOARD_SIZE = 15
CENTER_ROW = 7
CENTER_COL = 7
BINGO_BONUS = 50
RACK_SIZE = 7

# Distribution officielle francophone (102 jetons)
TILE_COUNTS = {
    'A': 9, 'B': 2, 'C': 2, 'D': 3, 'E': 15, 'F': 2, 'G': 2, 'H': 2,
    'I': 8, 'J': 1, 'K': 1, 'L': 5, 'M': 3, 'N': 6, 'O': 6, 'P': 2,
    'Q': 1, 'R': 6, 'S': 6, 'T': 6, 'U': 6, 'V': 2, 'W': 1, 'X': 1,
    'Y': 1, 'Z': 1, '?': 2
}

# Valeurs faciales des jetons
TILE_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 10, 'L': 1, 'M': 2, 'N': 1, 'O': 1, 'P': 3,
    'Q': 8, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 10, 'X': 10,
    'Y': 10, 'Z': 10, '?': 0
}

def tile_value(ch: str) -> int:
    """Retourne la valeur d'une lettre. Les minuscules représentent des jokers posés (0 pt)."""
    if ch.islower() or ch == '?':
        return 0
    return TILE_VALUES.get(ch, 0)

# Grille des multiplicateurs officiels : '' (normale), 'MT', 'MD', 'LT', 'LD'
_MT_COORDS = {
    (0, 0), (0, 7), (0, 14),
    (7, 0),         (7, 14),
    (14, 0), (14, 7), (14, 14)
}

_MD_COORDS = {
    (1, 1), (2, 2), (3, 3), (4, 4),
    (1, 13), (2, 12), (3, 11), (4, 10),
    (13, 1), (12, 2), (11, 3), (10, 4),
    (13, 13), (12, 12), (11, 11), (10, 10),
    (7, 7)
}

_LT_COORDS = {
    (1, 5), (1, 9),
    (5, 1), (5, 5), (5, 9), (5, 13),
    (9, 1), (9, 5), (9, 9), (9, 13),
    (13, 5), (13, 9)
}

_LD_COORDS = {
    (0, 3), (0, 11),
    (2, 6), (2, 8),
    (3, 0), (3, 7), (3, 14),
    (6, 2), (6, 6), (6, 8), (6, 12),
    (7, 3), (7, 11),
    (8, 2), (8, 6), (8, 8), (8, 12),
    (11, 0), (11, 7), (11, 14),
    (12, 6), (12, 8),
    (14, 3), (14, 11)
}

BOARD_BONUS: list[list[str]] = [['' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

for r in range(BOARD_SIZE):
    for c in range(BOARD_SIZE):
        coord = (r, c)
        if coord in _MT_COORDS:
            BOARD_BONUS[r][c] = 'MT'
        elif coord in _MD_COORDS:
            BOARD_BONUS[r][c] = 'MD'
        elif coord in _LT_COORDS:
            BOARD_BONUS[r][c] = 'LT'
        elif coord in _LD_COORDS:
            BOARD_BONUS[r][c] = 'LD'
