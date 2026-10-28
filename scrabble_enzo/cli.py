"""Module CLI autonome pour Scrabble Enzo (ODS8)."""

from __future__ import annotations
import argparse
import sys
from typing import List

from .constants import tile_value
from .board import Board
from .dictionary import ScrabbleDictionary
from .solver import MoveGenerator, Move
from .strategy import (
    EnzoStrategist,
    DuplicateGreedy,
    evaluate_leave,
    evaluate_defense_penalty,
)


def format_benjamins(dict_obj: ScrabbleDictionary, word: str) -> None:
    benjamins = dict_obj.find_benjamins(word)
    print(f"Benjamins (+3 lettres) pour '{word.upper()}' : {len(benjamins)} solution(s)")
    if benjamins:
        print(", ".join(benjamins))


def format_appuis(dict_obj: ScrabbleDictionary, rack: str) -> None:
    appuis = dict_obj.find_appuis_7_plus_1(rack)
    total_words = sum(len(words) for words in appuis.values())
    print(f"Appuis 7+1 pour '{rack.upper()}' : {len(appuis)} lettre(s) d'appui valide(s), {total_words} mot(s) au total")
    for letter in sorted(appuis.keys()):
        words = appuis[letter]
        words_sample = ", ".join(words[:15]) + ("..." if len(words) > 15 else "")
        print(f"  + {letter} ({len(words)}) : {words_sample}")


def format_avo(dict_obj: ScrabbleDictionary, prefix: str | None, top_avo: bool = False) -> None:
    if top_avo or (prefix is None or prefix == ""):
        top_list = dict_obj.top_prefixes_avo(3, 25)
        print(f"Top 25 des préfixes de 3 lettres les plus prolifiques (Jeu TV AVO) :")
        for rank, (pref, count) in enumerate(top_list, 1):
            print(f"  {rank:2d}. {pref} : {count} mots")
        return

    exts = dict_obj.find_prefix_extensions(prefix)
    print(f"Extensions AVO pour le préfixe '{prefix.upper()}' : {len(exts)} mot(s) trouvés")
    if not exts:
        return

    # Top mots les plus longs
    by_len = sorted(exts, key=lambda w: (len(w), sum(tile_value(c) for c in w)), reverse=True)
    # Top mots les plus chers
    by_score = sorted(exts, key=lambda w: (sum(tile_value(c) for c in w), len(w)), reverse=True)

    print("  Exemples de mots : " + ", ".join(exts[:20]) + ("..." if len(exts) > 20 else ""))
    print("  Mots les plus longs : " + ", ".join(f"{w} ({len(w)}L)" for w in by_len[:5]))
    print("  Mots les plus chers : " + ", ".join(f"{w} ({sum(tile_value(c) for c in w)} pts)" for w in by_score[:5]))


def format_solve(dict_obj: ScrabbleDictionary, generator: MoveGenerator, rack: str) -> None:
    board = Board()
    moves = generator.generate_all_moves(board, rack)
    print(f"Résolution pour le chevalet '{rack.upper()}' sur plateau initial : {len(moves)} coup(s) généré(s)")

    if not moves:
        print("  Aucun coup légal trouvé.")
        return

    # Classement Greedy (score brut)
    greedy_moves = sorted(moves, key=lambda m: m.score, reverse=True)[:5]
    print("\n--- Top 5 Coups : DuplicateGreedy (Score Brut) ---")
    for i, m in enumerate(greedy_moves, 1):
        print(f"  {i}. {m.coord_fisf} {m.word} : {m.score} pts (reliquat: '{m.leave}')")

    # Classement EnzoStrategist (équité = score + leave - défense)
    bag_count = board.total_remaining_tiles(rack)
    evaluated = []
    for m in moves[:100]:
        lv = evaluate_leave(m.leave)
        dp = evaluate_defense_penalty(board, m, bag_count)
        eq = round(m.score + lv - dp, 2)
        evaluated.append((m, eq, lv, dp))

    strat_moves = sorted(evaluated, key=lambda item: item[1], reverse=True)[:5]
    print("\n--- Top 5 Coups : EnzoStrategist (Équité Globale) ---")
    for i, (m, eq, lv, dp) in enumerate(strat_moves, 1):
        print(f"  {i}. {m.coord_fisf} {m.word} : {m.score} pts | Équité: {eq:+.2f} (reliquat: '{m.leave}' {lv:+.2f}, défense: -{dp:.2f})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrabble Enzo CLI — Solveur et entraîneur stratégique ODS8",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--benjamins", type=str, metavar="MOT", help="Affiche les Benjamins (+3 lettres) devant MOT")
    parser.add_argument("--appuis", type=str, metavar="LETTRES", help="Affiche les mots formables en 7+1 appuis")
    parser.add_argument("--avo", type=str, nargs="?", const="", default=None, metavar="PREFIXE", help="Recherche d'extensions AVO par préfixe")
    parser.add_argument("--avo-top", action="store_true", help="Classement des préfixes AVO de 3 lettres les plus prolifiques")
    parser.add_argument("--solve", type=str, metavar="CHEVALET", help="Résout le chevalet (Top 5 Greedy vs EnzoStrategist)")

    args = parser.parse_args()

    # Si aucun argument fourni, afficher l'aide
    if not (args.benjamins or args.appuis or args.avo is not None or args.avo_top or args.solve):
        parser.print_help()
        sys.exit(0)

    dict_obj = ScrabbleDictionary()
    generator = MoveGenerator(dict_obj)

    if args.benjamins:
        format_benjamins(dict_obj, args.benjamins)

    if args.appuis:
        format_appuis(dict_obj, args.appuis)

    if args.avo_top or args.avo is not None:
        format_avo(dict_obj, args.avo, top_avo=args.avo_top)

    if args.solve:
        format_solve(dict_obj, generator, args.solve)


if __name__ == "__main__":
    main()
