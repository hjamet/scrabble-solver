"""Générateur ultra-rapide et exhaustif de coups légaux sur le plateau 15x15."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Set, Tuple, Optional
import collections
from .constants import BOARD_SIZE, CENTER_ROW, CENTER_COL, BINGO_BONUS, BOARD_BONUS, TILE_VALUES, tile_value
from .board import Board
from .dictionary import ScrabbleDictionary

@dataclass
class Move:
    """Représentation d'un coup légal au Scrabble."""
    word: str
    row: int
    col: int
    horizontal: bool
    coord_fisf: str
    score: int
    tiles_placed: int
    leave: str
    cross_words: List[str] = field(default_factory=list)
    equity: float = 0.0
    leave_value: float = 0.0
    defense_penalty: float = 0.0
    opp_expected_max: float = 0.0

    def __repr__(self) -> str:
        dir_str = "H" if self.horizontal else "V"
        return f"<Move {self.coord_fisf} {self.word} ({self.score} pts, leave='{self.leave}')>"


class MoveGenerator:
    """Moteur de recherche exhaustif de coups basé sur les cross-checks et les Tries par longueur."""

    def __init__(self, dictionary: ScrabbleDictionary):
        self.dict = dictionary

    def generate_all_moves(self, board: Board, rack: str) -> List[Move]:
        """Génère tous les coups légaux possibles pour un plateau et un chevalet donnés."""
        rack = rack.upper()
        if not rack:
            return []

        board_empty = board.is_empty()
        moves_by_placement: Dict[Tuple[Tuple[int, int, str], ...], Move] = {}

        # 1. Coups horizontaux
        self._generate_directional_moves(board, rack, board_empty, horizontal=True, moves_by_placement=moves_by_placement)

        # 2. Coups verticaux (via transposition du plateau)
        transposed_board = self._transpose_board(board)
        transposed_moves: Dict[Tuple[Tuple[int, int, str], ...], Move] = {}
        self._generate_directional_moves(transposed_board, rack, board_empty, horizontal=False, moves_by_placement=transposed_moves)

        for signature, move in transposed_moves.items():
            if signature not in moves_by_placement:
                moves_by_placement[signature] = move

        all_moves = list(moves_by_placement.values())
        all_moves.sort(key=lambda m: m.score, reverse=True)
        return all_moves

    def _transpose_board(self, board: Board) -> Board:
        """Transpose la grille (lignes deviennent colonnes)."""
        t_grid = [[board.grid[c][r] for c in range(BOARD_SIZE)] for r in range(BOARD_SIZE)]
        return Board(t_grid)

    def _generate_directional_moves(
        self,
        board: Board,
        rack: str,
        board_empty: bool,
        horizontal: bool,
        moves_by_placement: Dict[Tuple[Tuple[int, int, str], ...], Move],
    ) -> None:
        grid = board.grid
        rack_counts = collections.Counter(rack)
        rack_len = len(rack)

        # Pré-calcul des cross-checks pour chaque case vide de la grille
        # cross_checks[r][c] = set de lettres majuscules autorisées, ou None si non contraint (toutes autorisées)
        cross_checks: List[List[Optional[Set[str]]]] = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        cross_scores: List[List[int]] = [[0 for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        cross_words_prefix_suffix: List[List[Tuple[str, str]]] = [[("", "") for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if grid[r][c] is not None:
                    continue
                # Vérifier les voisins verticaux sur la grille actuelle
                has_up = (r > 0 and grid[r - 1][c] is not None)
                has_down = (r < BOARD_SIZE - 1 and grid[r + 1][c] is not None)

                if not has_up and not has_down:
                    cross_checks[r][c] = None  # Pas de contrainte
                    continue

                # Construire le préfixe vers le haut
                up_tiles = []
                cur_r = r - 1
                while cur_r >= 0 and grid[cur_r][c] is not None:
                    up_tiles.append(grid[cur_r][c])
                    cur_r -= 1
                up_prefix = "".join(reversed(up_tiles)).upper()

                # Construire le suffixe vers le bas
                down_tiles = []
                cur_r = r + 1
                while cur_r < BOARD_SIZE and grid[cur_r][c] is not None:
                    down_tiles.append(grid[cur_r][c])
                    cur_r += 1
                down_suffix = "".join(down_tiles).upper()

                cross_words_prefix_suffix[r][c] = (up_prefix, down_suffix)

                # Score des lettres déjà posées sur la colonne
                base_score = sum(tile_value(t) for t in up_tiles) + sum(tile_value(t) for t in down_tiles)
                cross_scores[r][c] = base_score

                # Trouver les lettres valides pour compléter le mot
                valid_letters = set()
                for ord_ch in range(ord('A'), ord('Z') + 1):
                    ch = chr(ord_ch)
                    candidate = up_prefix + ch + down_suffix
                    if candidate in self.dict.words:
                        valid_letters.add(ch)

                cross_checks[r][c] = valid_letters

        # Parcours de chaque ligne
        for r in range(BOARD_SIZE):
            # Si le plateau est vide, seule la ligne centrale r == 7 peut contenir un mot
            if board_empty and r != CENTER_ROW:
                continue

            row_tiles = grid[r]

            for start_c in range(BOARD_SIZE):
                # Un mot ne peut pas démarrer immédiatement après une lettre déjà posée
                if start_c > 0 and row_tiles[start_c - 1] is not None:
                    continue

                for end_c in range(start_c + 1, min(BOARD_SIZE, start_c + 15)):
                    # Un mot ne peut pas se terminer immédiatement avant une lettre déjà posée
                    if end_c < BOARD_SIZE - 1 and row_tiles[end_c + 1] is not None:
                        continue

                    L = end_c - start_c + 1
                    if L not in self.dict.tries_by_len:
                        continue

                    # Vérifier le nombre de cases vides dans [start_c .. end_c]
                    vacant_indices = [c for c in range(start_c, end_c + 1) if row_tiles[c] is None]
                    num_vacant = len(vacant_indices)

                    if num_vacant == 0 or num_vacant > rack_len:
                        continue

                    # Vérifier la condition d'accroche (ancrage)
                    if board_empty:
                        if not (start_c <= CENTER_COL <= end_c):
                            continue
                    else:
                        touches_anchor = False
                        # Condition 1 : au moins une lettre est déjà sur la ligne dans ce segment
                        if num_vacant < L:
                            touches_anchor = True
                        else:
                            # Condition 2 : au moins une case vide a un voisin perpendiculaire
                            for vc in vacant_indices:
                                if cross_checks[r][vc] is not None:
                                    touches_anchor = True
                                    break
                            # Condition 3 : la case avant ou après touche une lettre
                            if not touches_anchor:
                                if start_c > 0 and row_tiles[start_c - 1] is not None:
                                    touches_anchor = True
                                elif end_c < BOARD_SIZE - 1 and row_tiles[end_c + 1] is not None:
                                    touches_anchor = True
                        if not touches_anchor:
                            continue

                    # Vérifier qu'aucune case vide n'a un cross-check impossible
                    impossible = False
                    for vc in vacant_indices:
                        if cross_checks[r][vc] is not None and len(cross_checks[r][vc]) == 0:
                            impossible = True
                            break
                    if impossible:
                        continue

                    # Explorer le Trie par longueur L
                    trie_root = self.dict.tries_by_len[L]
                    self._explore_segment(
                        r=r,
                        start_c=start_c,
                        end_c=end_c,
                        c=start_c,
                        node=trie_root,
                        row_tiles=row_tiles,
                        cross_checks=cross_checks,
                        cross_scores=cross_scores,
                        cross_words_prefix_suffix=cross_words_prefix_suffix,
                        rack_counts=dict(rack_counts),
                        word_chars=[],
                        placed_tiles=[],
                        horizontal=horizontal,
                        moves_by_placement=moves_by_placement,
                    )

    def _explore_segment(
        self,
        r: int,
        start_c: int,
        end_c: int,
        c: int,
        node: dict,
        row_tiles: List[Optional[str]],
        cross_checks: List[List[Optional[Set[str]]]],
        cross_scores: List[List[int]],
        cross_words_prefix_suffix: List[List[Tuple[str, str]]],
        rack_counts: Dict[str, int],
        word_chars: List[str],
        placed_tiles: List[Tuple[int, int, str]],
        horizontal: bool,
        moves_by_placement: Dict[Tuple[Tuple[int, int, str], ...], Move],
    ) -> None:
        if c > end_c:
            # Segment complété avec succès !
            word = "".join(word_chars)
            num_placed = len(placed_tiles)
            if num_placed == 0:
                return

            # Calcul du leave (lettres restantes)
            leave_list = []
            for letter, count in rack_counts.items():
                leave_list.extend([letter] * count)
            leave = "".join(sorted(leave_list))

            # Signature canonique basée sur les coordonnées réelles du plateau
            real_placed = []
            for pr, pc, pch in placed_tiles:
                if horizontal:
                    real_placed.append((pr, pc, pch))
                else:
                    real_placed.append((pc, pr, pch))
            signature = tuple(sorted(real_placed))

            if signature in moves_by_placement:
                return

            # Calcul du score exact
            real_row = r if horizontal else start_c
            real_col = start_c if horizontal else r
            score, cross_words = self._calculate_move_score(
                r=r,
                start_c=start_c,
                end_c=end_c,
                word=word,
                placed_tiles=placed_tiles,
                cross_scores=cross_scores,
                cross_words_prefix_suffix=cross_words_prefix_suffix,
                horizontal=horizontal,
            )

            coord_fisf = Board.format_coord_fisf(real_row, real_col, horizontal)
            move = Move(
                word=word,
                row=real_row,
                col=real_col,
                horizontal=horizontal,
                coord_fisf=coord_fisf,
                score=score,
                tiles_placed=num_placed,
                leave=leave,
                cross_words=cross_words,
            )
            moves_by_placement[signature] = move
            return

        existing_tile = row_tiles[c]
        if existing_tile is not None:
            # Case déjà occupée
            ch_upper = existing_tile.upper()
            if ch_upper in node:
                word_chars.append(existing_tile)
                self._explore_segment(
                    r, start_c, end_c, c + 1,
                    node[ch_upper], row_tiles, cross_checks, cross_scores,
                    cross_words_prefix_suffix, rack_counts, word_chars, placed_tiles,
                    horizontal, moves_by_placement
                )
                word_chars.pop()
        else:
            # Case vide : tester chaque lettre autorisée
            allowed = cross_checks[r][c]

            # 1. Tester les lettres normales du chevalet
            for letter, count in list(rack_counts.items()):
                if letter == '?' or count <= 0:
                    continue
                if letter not in node:
                    continue
                if allowed is not None and letter not in allowed:
                    continue

                rack_counts[letter] -= 1
                word_chars.append(letter)
                placed_tiles.append((r, c, letter))

                self._explore_segment(
                    r, start_c, end_c, c + 1,
                    node[letter], row_tiles, cross_checks, cross_scores,
                    cross_words_prefix_suffix, rack_counts, word_chars, placed_tiles,
                    horizontal, moves_by_placement
                )

                placed_tiles.pop()
                word_chars.pop()
                rack_counts[letter] += 1

            # 2. Tester le joker '?' s'il est présent
            if rack_counts.get('?', 0) > 0:
                rack_counts['?'] -= 1
                for letter, next_node in node.items():
                    if allowed is not None and letter not in allowed:
                        continue

                    # Le joker posé est noté en minuscule
                    joker_ch = letter.lower()
                    word_chars.append(joker_ch)
                    placed_tiles.append((r, c, joker_ch))

                    self._explore_segment(
                        r, start_c, end_c, c + 1,
                        next_node, row_tiles, cross_checks, cross_scores,
                        cross_words_prefix_suffix, rack_counts, word_chars, placed_tiles,
                        horizontal, moves_by_placement
                    )

                    placed_tiles.pop()
                    word_chars.pop()

                rack_counts['?'] += 1

    def _calculate_move_score(
        self,
        r: int,
        start_c: int,
        end_c: int,
        word: str,
        placed_tiles: List[Tuple[int, int, str]],
        cross_scores: List[List[int]],
        cross_words_prefix_suffix: List[List[Tuple[str, str]]],
        horizontal: bool,
    ) -> Tuple[int, List[str]]:
        """Calcule le score exact d'un coup selon les règles officielles du Scrabble."""
        placed_dict = {(pr, pc): pch for pr, pc, pch in placed_tiles}
        main_word_score = 0
        word_mult = 1
        cross_words: List[str] = []
        total_cross_score = 0

        for idx, c in enumerate(range(start_c, end_c + 1)):
            ch = word[idx]
            # Coordonnées réelles sur la grille originale pour récupérer les bonus
            real_r = r if horizontal else c
            real_c = c if horizontal else r

            if (r, c) in placed_dict:
                # Nouvelle lettre posée
                base_val = 0 if ch.islower() else TILE_VALUES.get(ch.upper(), 0)
                bonus = BOARD_BONUS[real_r][real_c]
                let_mult = 1
                if bonus == 'LD':
                    let_mult = 2
                elif bonus == 'LT':
                    let_mult = 3
                elif bonus == 'MD':
                    word_mult *= 2
                elif bonus == 'MT':
                    word_mult *= 3

                main_word_score += base_val * let_mult

                # Score du mot croisé perpendiculaire
                up_pre, down_suf = cross_words_prefix_suffix[r][c]
                if up_pre or down_suf:
                    cw = up_pre + ch.upper() + down_suf
                    cross_words.append(cw)
                    cw_base = cross_scores[r][c]
                    cw_let_val = base_val * let_mult
                    cw_mult = 1
                    if bonus == 'MD':
                        cw_mult = 2
                    elif bonus == 'MT':
                        cw_mult = 3
                    total_cross_score += (cw_base + cw_let_val) * cw_mult
            else:
                # Lettre déjà présente sur le plateau
                base_val = 0 if ch.islower() else TILE_VALUES.get(ch.upper(), 0)
                main_word_score += base_val

        final_score = (main_word_score * word_mult) + total_cross_score

        if len(placed_tiles) == 7:
            final_score += BINGO_BONUS

        return final_score, cross_words
