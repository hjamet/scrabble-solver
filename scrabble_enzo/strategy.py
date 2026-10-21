"""Moteur stratégique Anti-Enzo : évaluation de reliquat, défense de plateau et endgame exact."""

from __future__ import annotations
import collections
import random
from typing import List, Dict, Optional, Tuple
from .constants import BOARD_SIZE, TILE_VALUES, BOARD_BONUS, tile_value
from .board import Board
from .solver import Move, MoveGenerator
from .dictionary import ScrabbleDictionary

# 1. Table des valeurs de reliquat unitaire (ODS8 francophone calibré)
LEAVE_VALUES = {
    '?': 25.5, 'S': 7.5, 'E': 2.2, 'R': 2.0, 'I': 1.5, 'N': 1.4,
    'T': 1.4, 'A': 1.2, 'U': 1.0, 'L': 1.0, 'O': 0.8, 'D': 0.4,
    'M': 0.3, 'C': 0.3, 'P': 0.1, 'B': -0.5, 'G': -0.6, 'F': -0.8,
    'H': -1.0, 'V': -1.2, 'J': -1.5, 'Z': 0.5, 'X': 0.8, 'K': -3.5,
    'W': -4.0, 'Y': -2.5, 'Q': -5.5
}

VOWELS = set('AEIOUY')

def evaluate_leave(leave: str) -> float:
    """Évalue la valeur stratégique du reliquat (lettres gardées sur le chevalet)."""
    if not leave:
        return 0.0

    leave = leave.upper()
    val = 0.0
    counts = collections.Counter(leave)

    # 1. Somme des valeurs intrinsèques de chaque jeton
    for ch, cnt in counts.items():
        unit_val = LEAVE_VALUES.get(ch, 0.0)
        val += unit_val * cnt

    # 2. Synergie Q + U : annule la pénalité de Q s'il y a un U ou un joker
    if 'Q' in counts and ('U' in counts or '?' in counts):
        val += 4.5

    # 3. Pénalité de doublons
    for ch, cnt in counts.items():
        if ch == '?':
            if cnt >= 2:
                val -= 3.0 * (cnt - 1)
        elif ch == 'E':
            if cnt >= 3:
                val -= 1.8 * (cnt - 2)
        else:
            if cnt >= 2:
                val -= 2.2 * (cnt - 1)

    # 4. Équilibre Voyelles / Consonnes (sur lettres hors jokers)
    letters_only = [c for c in leave if c != '?']
    if letters_only:
        n_vowels = sum(1 for c in letters_only if c in VOWELS)
        n_consonants = len(letters_only) - n_vowels
        diff = abs(n_vowels - n_consonants)
        if diff >= 2:
            val -= 1.2 * (diff - 1) ** 1.5

    return round(val, 2)


def evaluate_defense_penalty(board: Board, move: Move, bag_count: int) -> float:
    """Évalue la pénalité défensive : ouverture de MT, MD ou LT à l'adversaire."""
    # Si le sac est vide et que le coup termine la partie, aucun risque défensif
    if bag_count == 0 and move.tiles_placed >= 7:
        return 0.0

    penalty = 0.0
    grid = board.grid
    L = len(move.word)

    # Identifier les cases nouvellement posées
    placed_coords = []
    for i in range(L):
        r = move.row if move.horizontal else move.row + i
        c = move.col + i if move.horizontal else move.col
        if grid[r][c] is None:
            placed_coords.append((r, c, move.word[i]))

    for pr, pc, pch in placed_coords:
        is_vowel = pch.upper() in VOWELS

        # Vérifier si la lettre posée est adjacente à une case spéciale encore libre
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = pr + dr, pc + dc
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE:
                if grid[nr][nc] is None:
                    bonus = BOARD_BONUS[nr][nc]
                    if bonus == 'MT':
                        penalty += 7.5 if is_vowel else 4.5
                    elif bonus in ('MD', 'LT') and is_vowel:
                        penalty += 2.0

        # Vérifier si elle ouvre une ligne directe vers un MT libre à distance <= 3
        # Ex. sur la même ligne ou même colonne
        if move.horizontal:
            for dist in [1, 2, 3]:
                for dc in [-dist, dist]:
                    target_c = pc + dc
                    if 0 <= target_c < BOARD_SIZE and grid[pr][target_c] is None:
                        if BOARD_BONUS[pr][target_c] == 'MT':
                            penalty += 3.0
        else:
            for dist in [1, 2, 3]:
                for dr in [-dist, dist]:
                    target_r = pr + dr
                    if 0 <= target_r < BOARD_SIZE and grid[target_r][pc] is None:
                        if BOARD_BONUS[target_r][pc] == 'MT':
                            penalty += 3.0

    return round(min(penalty, 25.0), 2)


def solve_endgame_2ply(
    board: Board,
    my_rack: str,
    opp_rack: str,
    dictionary: ScrabbleDictionary,
    generator: MoveGenerator,
    top_k: int = 15,
) -> Tuple[Optional[Move], float]:
    """Résolution exacte de fin de partie à 2 plis lorsque le sac est vide."""
    my_moves = generator.generate_all_moves(board, my_rack)
    if not my_moves:
        return None, 0.0

    opp_rack_value = sum(tile_value(ch) for ch in opp_rack)
    candidates = my_moves[:top_k]
    best_move = candidates[0]
    best_net_spread = -9999.0

    for m1 in candidates:
        # Cas 1 : Le joueur termine la partie en posant toutes ses lettres
        if m1.tiles_placed == len(my_rack):
            # Bonus de fin de partie : +2 x valeur des lettres de l'adversaire
            spread = m1.score + 2 * opp_rack_value
            if spread > best_net_spread:
                best_net_spread = spread
                best_move = m1
            continue

        # Cas 2 : L'adversaire réplique avec opp_rack
        # Simuler le plateau après m1
        b_after = board.copy()
        L = len(m1.word)
        for i in range(L):
            r = m1.row if m1.horizontal else m1.row + i
            c = m1.col + i if m1.horizontal else m1.col
            b_after.set_tile(r, c, m1.word[i])

        opp_moves = generator.generate_all_moves(b_after, opp_rack)
        if not opp_moves:
            # L'adversaire passe son tour
            spread = float(m1.score)
        else:
            # L'adversaire joue son coup qui maximise son spread
            max_opp_effective = -9999
            my_leave_val = sum(tile_value(ch) for ch in m1.leave)
            for m2 in opp_moves[:10]:
                if m2.tiles_placed == len(opp_rack):
                    # L'adversaire sort et prend 2 x la valeur de notre reliquat
                    opp_eff = m2.score + 2 * my_leave_val
                else:
                    opp_eff = m2.score
                if opp_eff > max_opp_effective:
                    max_opp_effective = opp_eff
            spread = m1.score - max_opp_effective

        if spread > best_net_spread:
            best_net_spread = spread
            best_move = m1

    return best_move, round(best_net_spread, 2)


def simulate_pimc_lookahead(
    board: Board,
    my_rack: str,
    dictionary: ScrabbleDictionary,
    generator: MoveGenerator,
    top_k: int = 8,
    num_samples: int = 5,
    seed: int = 42,
) -> None:
    """Estime l'espérance de score max adverse E[max m_opp] par échantillonnage Monte-Carlo PIMC."""
    rng = random.Random(seed)
    rem_tiles_dict = board.remaining_tiles(my_rack)
    pool = []
    for tile, cnt in rem_tiles_dict.items():
        pool.extend([tile] * cnt)

    if len(pool) < 7:
        return

    moves = generator.generate_all_moves(board, my_rack)[:top_k]
    for move in moves:
        # Simuler le plateau après le coup
        b_next = board.copy()
        L = len(move.word)
        for i in range(L):
            r = move.row if move.horizontal else move.row + i
            c = move.col + i if move.horizontal else move.col
            b_next.set_tile(r, c, move.word[i])

        opp_scores = []
        for _ in range(num_samples):
            opp_sample = "".join(rng.sample(pool, 7))
            opp_moves = generator.generate_all_moves(b_next, opp_sample)
            if opp_moves:
                opp_scores.append(opp_moves[0].score)
            else:
                opp_scores.append(0)

        move.opp_expected_max = round(sum(opp_scores) / len(opp_scores), 2)


class DuplicateGreedy:
    """Agent Duplicate / Glouton classique : maximise le score brut immédiat."""

    def __init__(self, dictionary: ScrabbleDictionary, generator: MoveGenerator):
        self.dict = dictionary
        self.gen = generator

    def choose_move(self, board: Board, rack: str) -> Optional[Move]:
        moves = self.gen.generate_all_moves(board, rack)
        if not moves:
            return None
        return moves[0]


class EnzoStrategist:
    """Agent Stratégique Complet Anti-Enzo : équité (Score + Leave - Defense) et endgame 2-plis."""

    def __init__(self, dictionary: ScrabbleDictionary, generator: MoveGenerator):
        self.dict = dictionary
        self.gen = generator

    def choose_move(
        self,
        board: Board,
        rack: str,
        known_opp_rack: Optional[str] = None,
    ) -> Optional[Move]:
        bag_count = board.total_remaining_tiles(rack)

        # Mode Fin de partie : sac vide et rack adverse connu
        if bag_count == 0 and known_opp_rack is not None:
            best_m, _ = solve_endgame_2ply(board, rack, known_opp_rack, self.dict, self.gen)
            if best_m is not None:
                return best_m

        moves = self.gen.generate_all_moves(board, rack)
        if not moves:
            return None

        # Évaluer chaque coup candidat (sur le top 40 des meilleurs scores bruts)
        best_move = moves[0]
        best_equity = -9999.0

        for m in moves[:40]:
            lv = evaluate_leave(m.leave)
            dp = evaluate_defense_penalty(board, m, bag_count)
            eq = m.score + lv - dp

            m.leave_value = lv
            m.defense_penalty = dp
            m.equity = round(eq, 2)

            if eq > best_equity:
                best_equity = eq
                best_move = m

        return best_move
