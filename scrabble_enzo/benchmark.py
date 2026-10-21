"""Benchmark expérimental complet et reproductible : EnzoStrategist vs DuplicateGreedy."""

from __future__ import annotations
import copy
import json
import os
import random
import time
from typing import Dict, List, Any
from .constants import TILE_COUNTS, TILE_VALUES, tile_value
from .board import Board
from .dictionary import ScrabbleDictionary
from .solver import MoveGenerator
from .strategy import DuplicateGreedy, EnzoStrategist

class ScrabbleGameSimulator:
    """Simulateur officiel de partie 1 contre 1 entre deux agents."""

    def __init__(self, dictionary: ScrabbleDictionary, generator: MoveGenerator, seed: int = 42):
        self.dict = dictionary
        self.gen = generator
        self.rng = random.Random(seed)

    def _init_bag(self) -> List[str]:
        bag = []
        for tile, count in TILE_COUNTS.items():
            bag.extend([tile] * count)
        self.rng.shuffle(bag)
        return bag

    def play_game(self, strategist_first: bool) -> Dict[str, Any]:
        """Joue une partie complète et retourne les métriques."""
        bag = self._init_bag()
        board = Board()
        greedy_agent = DuplicateGreedy(self.dict, self.gen)
        strat_agent = EnzoStrategist(self.dict, self.gen)

        rack_strat = "".join([bag.pop() for _ in range(min(7, len(bag)))])
        rack_greedy = "".join([bag.pop() for _ in range(min(7, len(bag)))])

        score_strat = 0
        score_greedy = 0
        bingos_strat = 0
        bingos_greedy = 0

        consecutive_passes = 0
        turns = 0
        strat_turn = strategist_first
        move_times = []

        while consecutive_passes < 6:
            current_rack = rack_strat if strat_turn else rack_greedy
            t0 = time.perf_counter()

            if strat_turn:
                # Mode fin de partie : si le sac est vide, le rack adverse est connu
                known_opp = rack_greedy if len(bag) == 0 else None
                move = strat_agent.choose_move(board, current_rack, known_opp)
            else:
                move = greedy_agent.choose_move(board, current_rack)

            t1 = time.perf_counter()
            move_times.append(t1 - t0)

            if move is None:
                consecutive_passes += 1
                # Tentative d'échange si sac >= 7
                if len(bag) >= 7 and len(current_rack) > 0:
                    # Échange toutes les lettres
                    returned = list(current_rack)
                    new_rack = "".join([bag.pop() for _ in range(len(returned))])
                    bag.extend(returned)
                    self.rng.shuffle(bag)
                    if strat_turn:
                        rack_strat = new_rack
                    else:
                        rack_greedy = new_rack
            else:
                consecutive_passes = 0
                turns += 1

                # Appliquer le coup sur le plateau
                L = len(move.word)
                for i in range(L):
                    r = move.row if move.horizontal else move.row + i
                    c = move.col + i if move.horizontal else move.col
                    board.set_tile(r, c, move.word[i])

                # Mettre à jour le score et les bingos
                if strat_turn:
                    score_strat += move.score
                    if move.tiles_placed == 7:
                        bingos_strat += 1
                    # Nouveau rack
                    needed = 7 - len(move.leave)
                    drawn = "".join([bag.pop() for _ in range(min(needed, len(bag)))])
                    rack_strat = move.leave + drawn
                else:
                    score_greedy += move.score
                    if move.tiles_placed == 7:
                        bingos_greedy += 1
                    needed = 7 - len(move.leave)
                    drawn = "".join([bag.pop() for _ in range(min(needed, len(bag)))])
                    rack_greedy = move.leave + drawn

                # Vérifier la condition de fin immédiate (chevalet vide et sac vide)
                if len(bag) == 0:
                    if strat_turn and len(rack_strat) == 0:
                        # EnzoStrategist sort : bonus de 2x la valeur restante chez Greedy
                        opp_rem_val = sum(tile_value(ch) for ch in rack_greedy)
                        score_strat += 2 * opp_rem_val
                        break
                    elif not strat_turn and len(rack_greedy) == 0:
                        # Greedy sort : bonus de 2x la valeur restante chez Strategist
                        opp_rem_val = sum(tile_value(ch) for ch in rack_strat)
                        score_greedy += 2 * opp_rem_val
                        break

            strat_turn = not strat_turn

        # Si partie bloquée par passes consécutives
        if consecutive_passes >= 6:
            score_strat -= sum(tile_value(ch) for ch in rack_strat)
            score_greedy -= sum(tile_value(ch) for ch in rack_greedy)

        winner = "Strategist" if score_strat > score_greedy else ("Greedy" if score_greedy > score_strat else "Draw")
        spread = score_strat - score_greedy

        return {
            "first_player": "Strategist" if strategist_first else "Greedy",
            "score_strategist": score_strat,
            "score_greedy": score_greedy,
            "winner": winner,
            "spread": spread,
            "bingos_strategist": bingos_strat,
            "bingos_greedy": bingos_greedy,
            "turns": turns,
            "avg_move_time_ms": round((sum(move_times) / max(1, len(move_times))) * 1000, 2),
        }


def run_benchmark(num_games: int = 30, base_seed: int = 42) -> Dict[str, Any]:
    """Exécute les N parties appariées et retourne le rapport statistique."""
    print("Chargement du dictionnaire ODS8 et du solveur...")
    d = ScrabbleDictionary()
    gen = MoveGenerator(d)

    results = []
    print(f"Lancement du benchmark : {num_games} parties appariées (alternance 1er joueur)...")

    for i in range(num_games):
        seed = base_seed + i
        sim = ScrabbleGameSimulator(d, gen, seed=seed)
        # Alternance stricte : Strategist commence les parties paires, Greedy les impaires
        strat_first = (i % 2 == 0)
        game_res = sim.play_game(strategist_first=strat_first)
        game_res["game_id"] = i + 1
        game_res["seed"] = seed
        results.append(game_res)
        print(
            f"Partie {i+1:2d}/{num_games:2d} | 1er: {game_res['first_player'][:4]} | "
            f"Strat: {game_res['score_strategist']:3d} vs Greedy: {game_res['score_greedy']:3d} | "
            f"Vainqueur: {game_res['winner']:10s} | Spread: {game_res['spread']:+4d} | "
            f"Bingos: {game_res['bingos_strategist']}-{game_res['bingos_greedy']}"
        )

    # Agrégations statistiques
    strat_wins = sum(1 for r in results if r["winner"] == "Strategist")
    greedy_wins = sum(1 for r in results if r["winner"] == "Greedy")
    draws = sum(1 for r in results if r["winner"] == "Draw")

    avg_score_strat = sum(r["score_strategist"] for r in results) / num_games
    avg_score_greedy = sum(r["score_greedy"] for r in results) / num_games
    avg_spread = sum(r["spread"] for r in results) / num_games
    avg_bingos_strat = sum(r["bingos_strategist"] for r in results) / num_games
    avg_bingos_greedy = sum(r["bingos_greedy"] for r in results) / num_games
    avg_move_time = sum(r["avg_move_time_ms"] for r in results) / num_games

    win_rate_strat = (strat_wins / num_games) * 100.0

    summary = {
        "num_games": num_games,
        "base_seed": base_seed,
        "strategist_wins": strat_wins,
        "greedy_wins": greedy_wins,
        "draws": draws,
        "strategist_win_rate_pct": round(win_rate_strat, 1),
        "avg_score_strategist": round(avg_score_strat, 1),
        "avg_score_greedy": round(avg_score_greedy, 1),
        "avg_spread": round(avg_spread, 1),
        "avg_bingos_strategist": round(avg_bingos_strat, 2),
        "avg_bingos_greedy": round(avg_bingos_greedy, 2),
        "avg_move_time_ms": round(avg_move_time, 2),
        "games": results,
    }

    # Sauvegarder dans results/benchmark_greedy_vs_strategy.json
    results_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(results_dir, exist_ok=True)
    out_file = os.path.join(results_dir, "benchmark_greedy_vs_strategy.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("RÉSUMÉ DU BENCHMARK EXPERIMENTAL")
    print("=" * 60)
    print(f"Nombre de parties     : {num_games}")
    print(f"Victoires Strategist : {strat_wins} ({win_rate_strat:.1f}%)")
    print(f"Victoires Greedy     : {greedy_wins} ({(greedy_wins/num_games)*100.0:.1f}%)")
    print(f"Nuls                 : {draws}")
    print(f"Score moyen Strat    : {avg_score_strat:.1f} pts")
    print(f"Score moyen Greedy   : {avg_score_greedy:.1f} pts")
    print(f"Spread moyen net     : {avg_spread:+.1f} pts")
    print(f"Bingos moyens (Strat): {avg_bingos_strat:.2f} par partie")
    print(f"Bingos moyens (Greedy): {avg_bingos_greedy:.2f} par partie")
    print(f"Temps moyen / coup   : {avg_move_time:.2f} ms")
    print(f"Résultats enregistrés: {out_file}")
    print("=" * 60)

    return summary

if __name__ == "__main__":
    run_benchmark(num_games=30, base_seed=42)
