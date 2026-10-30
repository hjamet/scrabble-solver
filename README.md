# Scrabble Enzo — Solveur & Moteur Stratégique ODS8

Solveur, entraîneur et arbitre stratégique de Scrabble francophone basé sur le lexique officiel ODS8 (411 430 mots) et la distribution francophone de 102 jetons.

## Fonctionnalités Principales

### 1. Moteur Stratégique Anti-Enzo (`EnzoStrategist`)
- **Évaluation de reliquat centrée** (`LEAVE_VALUES`) : espérance nulle sur le sac, synergie $Q + U$, bonus majeurs ($S$, $?$) et pénalités de doublons.
- **Pénalité défensive de plateau** : détection de l'exposition immédiate de cases Mot Triple (`MT`) ou Mot Double (`MD`).
- **Solveur Endgame 2-Plis** : déduction automatique du chevalet adverse dès que le sac est vide ($\le 7$ jetons non vus) et minimisation du spread net.
- **Échange stratégique optimal** (`evaluate_best_exchange`) : arbitrage automatique entre coup sur plateau et échange de lettres à reliquat négatif.

### 2. Mode « Partie Réelle » & Arbitre ODS8 (Interface Web)
- **Saisie directe au clavier sur la grille 15×15** (zéro `prompt()` bloquant) : sélection de case, indicateur d'orientation `→`/`↓`, auto-incrémentation, jokers en minuscule via `Shift`, effacement et navigation au clavier.
- **Scoreboard en direct** (Nous vs Enzo & Loïc) : suivi des scores cumulés, différentiel de points et historique des coups.
- **Validation & Contestation ODS8 de coup adverse** (`/api/play_move`) : pose de coordonnées FISF (ex. `8D`, `H4`), détection des mots croisés perpendiculaires, calcul du score officiel et alerte rouge vif immédiate en cas de mot non valide ODS8 avec bouton `↩️ Annuler`.
- **Bandeau de conseil stratégique** : alertes en temps réel pour échange recommandé et tirage déduit en fin de partie.
- **Persistance automatique** : reprise transparente de la partie active via `localStorage` et pile d'annulation complète (`undoStack`).

### 3. Entraînement de Champion
- **Appuis 7+1** : recherche instantanée des rallonges par lettre sur tirages de 7 lettres.
- **Benjamins (+3 lettres)** : découverte des préfixes de 3 lettres sur mot de base.
- **Spécial TV AVO** : extensions de préfixes et Top 25 des racines ODS8.
- **Anagrammes exhaustives** : recherche ultra-rapide par Trie global et tables d'alphagrammes.

## Lancement

### Application Web
```bash
python -m scrabble_enzo.web_app
# ou double-clic sur lancer_scrabble_enzo.bat
```
Disponible sur `http://127.0.0.1:8765`.

### Ligne de Commande (CLI)
```bash
# Résoudre une position
python -m scrabble_enzo.cli --solve TIREURS

# Entraînement Benjamins, Appuis, AVO
python -m scrabble_enzo.cli --benjamins TABLE
python -m scrabble_enzo.cli --appuis AELRST
python -m scrabble_enzo.cli --avo DEC
```

### Tests & Benchmark
```bash
pytest -v
python -m scrabble_enzo.benchmark
```
