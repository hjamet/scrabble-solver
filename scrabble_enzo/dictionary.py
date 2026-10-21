"""Module de dictionnaire ODS8 et structures d'indexation pour le Scrabble."""

from __future__ import annotations
import collections
import itertools
import os
import pickle
from typing import Dict, List, Set, Tuple, Optional

_TRIE_END = '*'

class ScrabbleDictionary:
    """Index ODS8 complet avec Trie par longueur, Trie global et Alphagrammes."""

    def __init__(self, ods_path: Optional[str] = None):
        if ods_path is None:
            # Emplacement par défaut par rapport au package
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            ods_path = os.path.join(base_dir, "data", "ods8.txt")
        self.ods_path = ods_path
        self.words: Set[str] = set()
        self.words_by_len: Dict[int, Set[str]] = collections.defaultdict(set)
        self.tries_by_len: Dict[int, dict] = {L: {} for L in range(2, 16)}
        self.global_trie: dict = {}
        self.alphagrams: Dict[str, List[str]] = collections.defaultdict(list)
        self._load()

    def _load(self) -> None:
        cache_path = os.path.splitext(self.ods_path)[0] + ".pkl"
        # Si le cache existe et est plus récent que le fichier texte
        if (
            os.path.exists(cache_path)
            and os.path.exists(self.ods_path)
            and os.path.getmtime(cache_path) >= os.path.getmtime(self.ods_path)
        ):
            try:
                with open(cache_path, "rb") as f:
                    data = pickle.load(f)
                    self.words = data["words"]
                    self.words_by_len = data["words_by_len"]
                    self.tries_by_len = data["tries_by_len"]
                    self.global_trie = data["global_trie"]
                    self.alphagrams = data["alphagrams"]
                    return
            except Exception:
                pass  # Recharger depuis le fichier texte

        if not os.path.exists(self.ods_path):
            raise FileNotFoundError(f"Dictionnaire ODS introuvable à {self.ods_path}")

        with open(self.ods_path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().upper()
                if not w:
                    continue
                self.words.add(w)
                L = len(w)
                self.words_by_len[L].add(w)
                self.alphagrams["".join(sorted(w))].append(w)

                # Insertion dans Trie global
                curr_g = self.global_trie
                for ch in w:
                    curr_g = curr_g.setdefault(ch, {})
                curr_g[_TRIE_END] = True

                # Insertion dans Trie par longueur si L <= 15
                if 2 <= L <= 15:
                    curr_len = self.tries_by_len[L]
                    for ch in w:
                        curr_len = curr_len.setdefault(ch, {})

        # Sauvegarder dans le cache pour les démarrages suivants
        try:
            with open(cache_path, "wb") as f:
                pickle.dump(
                    {
                        "words": self.words,
                        "words_by_len": self.words_by_len,
                        "tries_by_len": self.tries_by_len,
                        "global_trie": self.global_trie,
                        "alphagrams": dict(self.alphagrams),
                    },
                    f,
                    protocol=pickle.HIGHEST_PROTOCOL,
                )
        except Exception:
            pass

    def is_word(self, word: str) -> bool:
        """Vérifie si le mot appartient à l'ODS8."""
        return word.upper() in self.words

    def find_anagrams(self, rack: str, min_len: int = 2, max_len: int = 15) -> List[str]:
        """Trouve tous les mots formables avec le chevalet (supporte ?)."""
        rack = rack.upper()
        num_jokers = rack.count('?')
        letters = sorted([c for c in rack if c != '?'])

        results: Set[str] = set()

        if num_jokers == 0:
            # Recherche directe par sous-alphagrammes
            max_k = min(len(letters), max_len)
            for k in range(min_len, max_k + 1):
                seen_sub = set()
                for comb in itertools.combinations(letters, k):
                    sub_alpha = "".join(comb)
                    if sub_alpha in seen_sub:
                        continue
                    seen_sub.add(sub_alpha)
                    if sub_alpha in self.alphagrams:
                        results.update(self.alphagrams[sub_alpha])
            return sorted(results)

        # Avec jokers : énumération par substitution ou DFS sur global_trie
        def dfs(node: dict, path: List[str], current_rack: List[str], jokers_left: int):
            if _TRIE_END in node and min_len <= len(path) <= max_len:
                results.add("".join(path))
            if len(path) >= max_len:
                return

            # Option 1 : utiliser une lettre du chevalet
            used_chars = set()
            for i, ch in enumerate(current_rack):
                if ch in used_chars:
                    continue
                used_chars.add(ch)
                if ch in node:
                    dfs(node[ch], path + [ch], current_rack[:i] + current_rack[i+1:], jokers_left)

            # Option 2 : utiliser un joker
            if jokers_left > 0:
                for ch, next_node in node.items():
                    if ch == _TRIE_END:
                        continue
                    dfs(next_node, path + [ch], current_rack, jokers_left - 1)

        dfs(self.global_trie, [], letters, num_jokers)
        return sorted(results)

    def find_appuis_7_plus_1(self, rack: str) -> Dict[str, List[str]]:
        """Trouve pour chaque lettre A-Z les mots de 7 ou 8 lettres formables."""
        rack = rack.upper()
        appuis: Dict[str, List[str]] = {}
        for ord_c in range(ord('A'), ord('Z') + 1):
            letter = chr(ord_c)
            # Rack étendu avec la lettre d'appui
            words = self.find_anagrams(rack + letter, min_len=7, max_len=8)
            # Ne garder que ceux qui utilisent la lettre d'appui
            # (si le rack ne la contenait pas, ou s'il en utilise plus que dans le rack)
            valid = [w for w in words if letter in w]
            if valid:
                appuis[letter] = valid
        return appuis

    def find_benjamins(self, word: str) -> List[str]:
        """Trouve tous les mots de len(word) + 3 se terminant par word (rallonges de 3 lettres en tête)."""
        word = word.upper()
        target_len = len(word) + 3
        if target_len not in self.words_by_len:
            return []
        res = [w for w in self.words_by_len[target_len] if w.endswith(word)]
        return sorted(res)

    def find_prefix_extensions(self, prefix: str, min_len: int = 2, max_len: int = 15) -> List[str]:
        """Trouve tous les mots commençant par un préfixe donné."""
        prefix = prefix.upper()
        curr = self.global_trie
        for ch in prefix:
            if ch not in curr:
                return []
            curr = curr[ch]

        results: List[str] = []

        def dfs(node: dict, path: List[str]):
            L = len(path)
            if _TRIE_END in node and min_len <= L <= max_len:
                results.append("".join(path))
            if L >= max_len:
                return
            for ch, next_node in node.items():
                if ch == _TRIE_END:
                    continue
                dfs(next_node, path + [ch])

        dfs(curr, list(prefix))
        return sorted(results)

    def top_prefixes_avo(self, prefix_len: int = 3, top_k: int = 25) -> List[Tuple[str, int]]:
        """Retourne les préfixes de taille prefix_len ayant le plus d'extensions (jeu TV AVO)."""
        counts: Dict[str, int] = collections.defaultdict(int)
        for w in self.words:
            if len(w) >= prefix_len:
                counts[w[:prefix_len]] += 1
        sorted_prefixes = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        return sorted_prefixes[:top_k]
