"""Serveur HTTP local autonome et interface Web interactive pour Scrabble Enzo (ODS8)."""

from __future__ import annotations
import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, List
from .constants import BOARD_SIZE, BOARD_BONUS, TILE_COUNTS, TILE_VALUES, tile_value
from .board import Board
from .dictionary import ScrabbleDictionary
from .solver import MoveGenerator, Move
from .strategy import EnzoStrategist, evaluate_leave, evaluate_defense_penalty, solve_endgame_2ply

# Instance globale partagée du dictionnaire et du solveur
_GLOBAL_DICT: ScrabbleDictionary | None = None
_GLOBAL_GEN: MoveGenerator | None = None

def get_shared_engine() -> tuple[ScrabbleDictionary, MoveGenerator]:
    global _GLOBAL_DICT, _GLOBAL_GEN
    if _GLOBAL_DICT is None:
        _GLOBAL_DICT = ScrabbleDictionary()
        _GLOBAL_GEN = MoveGenerator(_GLOBAL_DICT)
    return _GLOBAL_DICT, _GLOBAL_GEN


HTML_PAGE = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scrabble Enzo — Solveur & Moteur Stratégique ODS8</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🔠</text></svg>">
    <style>
        :root {
            --bg-dark: #12151c;
            --bg-card: #1c2230;
            --bg-card-hover: #232b3d;
            --accent-gold: #f59e0b;
            --accent-blue: #3b82f6;
            --accent-green: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --board-bg: #0f2d1e;
            --tile-bg: #fef3c7;
            --tile-text: #1f2937;
            --c-mt: #dc2626;
            --c-md: #fb7185;
            --c-lt: #1d4ed8;
            --c-ld: #38bdf8;
            --c-normal: #154a32;
        }
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        body { background: var(--bg-dark); color: var(--text-main); min-height: 100vh; padding: 16px; display: flex; flex-direction: column; margin: 0; overflow-x: hidden; }
        header { display: flex; align-items: center; justify-content: space-between; padding: 8px 16px; background: var(--bg-card); border-radius: 8px; margin: 0 auto 16px auto; max-width: 1360px; width: 100%; border-left: 5px solid var(--accent-gold); }
        h1 { font-size: 1.3rem; font-weight: 700; color: #fff; }
        .badge { background: #374151; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; color: var(--accent-gold); font-weight: 600; white-space: nowrap; }
        .main-layout { max-width: 1360px; width: 100%; margin: 0 auto; padding: 12px 16px; display: grid; grid-template-columns: 520px minmax(0, 1fr); gap: 16px; align-items: start; }
        
        /* Plateau Scrabble */
        .board-container { background: var(--board-bg); padding: 6px; border-radius: 10px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); user-select: none; width: 520px; }
        .scrabble-board { display: grid; grid-template-columns: repeat(15, 32px); grid-template-rows: repeat(15, 32px); gap: 2px; }
        .cell {
            width: 32px; height: 32px; display: flex; flex-direction: column; align-items: center; justify-content: center;
            font-size: 10px; font-weight: 700; border-radius: 3px; cursor: pointer; position: relative; transition: transform 0.1s;
        }
        .cell:hover { outline: 2px solid #fff; z-index: 2; }
        .cell.MT { background: var(--c-mt); color: #fff; }
        .cell.MD { background: var(--c-md); color: #fff; }
        .cell.LT { background: var(--c-lt); color: #fff; }
        .cell.LD { background: var(--c-ld); color: #fff; }
        .cell.normal { background: var(--c-normal); color: #047857; }
        
        .cell.has-tile { background: var(--tile-bg); color: var(--tile-text); border: 1px solid #d97706; }
        .cell.has-tile .tile-letter { font-size: 16px; font-weight: 900; line-height: 1; }
        .cell.has-tile .tile-value { font-size: 9px; position: absolute; bottom: 2px; right: 3px; font-weight: 700; color: #4b5563; }
        .cell.is-joker .tile-letter { color: #dc2626; }
        .cell.preview-tile { background: #a7f3d0 !important; color: #064e3b !important; outline: 2px dashed #059669; }
        
        /* Panneau de Contrôle Latéral */
        .sidebar { display: flex; flex-direction: column; gap: 16px; min-width: 0; width: 100%; }
        .card { background: var(--bg-card); border-radius: 8px; padding: 14px; border: 1px solid #2d3748; min-width: 0; width: 100%; }
        .card h2 { font-size: 1rem; margin-bottom: 10px; color: var(--accent-gold); display: flex; align-items: center; justify-content: space-between; }
        
        .rack-input-row, .train-input-row { display: flex; gap: 8px; margin-bottom: 10px; width: 100%; }
        input[type="text"] {
            background: #111827; border: 1px solid #374151; color: #fff; padding: 8px 12px; border-radius: 6px;
            font-size: 1.1rem; text-transform: uppercase; font-weight: 700; letter-spacing: 2px; flex: 1; min-width: 0;
        }
        input[type="text"]:focus { outline: none; border-color: var(--accent-gold); }
        button {
            background: var(--accent-gold); color: #111; font-weight: 700; border: none; padding: 8px 16px; border-radius: 6px;
            cursor: pointer; transition: background 0.15s, transform 0.05s; display: inline-flex; align-items: center; justify-content: center; gap: 6px;
            flex-shrink: 0; white-space: nowrap;
        }
        button:hover { background: #d97706; }
        button:active { transform: scale(0.98); }
        button.secondary { background: #374151; color: #fff; }
        button.secondary:hover { background: #4b5563; }
        
        /* Résultats */
        .results-table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 8px; table-layout: auto; }
        .results-table th { text-align: left; padding: 6px 8px; background: #111827; color: var(--text-muted); font-size: 0.75rem; white-space: nowrap; }
        .results-table td { padding: 6px 8px; border-bottom: 1px solid #2d3748; white-space: nowrap; }
        .results-table tr:hover { background: var(--bg-card-hover); cursor: pointer; }
        .score-pill { font-weight: 800; color: var(--accent-green); }
        .equity-pill { font-weight: 800; color: var(--accent-gold); }
        
        /* Sac & Statistiques */
        .bag-grid { display: grid; grid-template-columns: repeat(9, minmax(0, 1fr)); gap: 6px; font-size: 0.75rem; text-align: center; width: 100%; }
        .bag-item { background: #111827; padding: 4px 2px; border-radius: 4px; border: 1px solid #374151; min-width: 0; }
        .bag-item.empty { opacity: 0.3; }
        .bag-count { font-weight: 700; color: var(--accent-gold); }

        /* Onglets d'Entraînement */
        .tab-buttons { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 10px; width: 100%; }
        .tab-btn { flex: 1; min-width: 0; padding: 6px 8px; font-size: 0.75rem; background: #1f2937; color: var(--text-muted); border: none; border-radius: 4px; cursor: pointer; white-space: nowrap; text-align: center; }
        .tab-btn.active { background: var(--accent-blue); color: #fff; font-weight: 700; }
        .train-content { display: none; font-size: 0.85rem; max-height: 220px; overflow-y: auto; }
        .train-content.active { display: block; }
        .pill-list { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
        .pill, .tag { background: #374151; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: 600; color: #f3f4f6; }
    </style>
</head>
<body>
    <header>
        <div>
            <h1>Scrabble Enzo <span style="font-weight: 400; font-size: 0.9rem; color: #9ca3af;">— Moteur Stratégique ODS8 Francophone</span></h1>
        </div>
        <div style="display: flex; gap: 10px; align-items: center;">
            <span class="badge">411 430 mots ODS8</span>
            <span class="badge">102 Jetons</span>
            <span class="badge" id="speed-badge">Prêt</span>
        </div>
    </header>

    <div class="main-layout">
        <!-- Plateau -->
        <div class="board-container">
            <div class="scrabble-board" id="board"></div>
            <div style="margin-top: 10px; display: flex; justify-content: space-between; align-items: center;">
                <button class="secondary" onclick="clearBoard()">Vider le plateau</button>
                <span style="font-size: 0.78rem; color: #9ca3af;">Clic sur case : poser lettre (maj/min/vide)</span>
            </div>
        </div>

        <!-- Panneau latéral -->
        <div class="sidebar">
            <!-- Saisie Chevalet & Résolution -->
            <div class="card">
                <h2>Chevalet & Résolution Stratégique</h2>
                <div class="rack-input-row">
                    <input type="text" id="rack-input" maxlength="7" placeholder="EX: TIREUR?" value="TIREUR?">
                    <button onclick="solvePosition()">⚡ Résoudre</button>
                </div>
                <div style="display: flex; gap: 6px;">
                    <button class="secondary" style="flex:1;" onclick="applyTopMove()">Poser Top Coup</button>
                    <button class="secondary" style="flex:1;" onclick="clearPreview()">Effacer Aperçu</button>
                </div>

                <!-- Résultats des coups -->
                <div style="margin-top: 12px; max-height: 260px; overflow-y: auto;">
                    <table class="results-table">
                        <thead>
                            <tr>
                                <th>Réf</th>
                                <th>Mot</th>
                                <th>Pts</th>
                                <th>Reliquat</th>
                                <th>Équité</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody id="moves-tbody">
                            <tr><td colspan="6" style="text-align: center; color: #6b7280;">Saisissez un chevalet et cliquez sur Résoudre.</td></tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Décompte du Sac (102 jetons) -->
            <div class="card">
                <h2><span>Jetons Non Vus (<span id="unseen-count">102</span>)</span></h2>
                <div class="bag-grid" id="bag-grid"></div>
            </div>

            <!-- Panneau Entraînement Champion -->
            <div class="card">
                <h2>Entraînement de Champion</h2>
                <div class="tab-buttons">
                    <button class="tab-btn active" onclick="switchTab('appuis')">Appuis 7+1</button>
                    <button class="tab-btn" onclick="switchTab('benjamins')">Benjamins (+3)</button>
                    <button class="tab-btn" onclick="switchTab('avo')">Spécial AVO</button>
                    <button class="tab-btn" onclick="switchTab('anagrams')">Anagrammes</button>
                </div>

                <!-- Onglet Appuis 7+1 -->
                <div id="tab-appuis" class="train-content active">
                    <div class="train-input-row">
                        <input type="text" id="appuis-input" maxlength="7" placeholder="Chevalet 7 let." value="AELRST">
                        <button onclick="searchAppuis()">Chercher</button>
                    </div>
                    <div id="appuis-results" class="train-results" style="margin-top: 8px;"></div>
                </div>

                <!-- Onglet Benjamins -->
                <div id="tab-benjamins" class="train-content">
                    <div class="train-input-row">
                        <input type="text" id="benjamins-input" placeholder="Mot base (ex. TABLE)" value="TABLE">
                        <button onclick="searchBenjamins()">Chercher</button>
                    </div>
                    <div id="benjamins-results" class="train-results" style="margin-top: 8px;"></div>
                </div>

                <!-- Onglet AVO -->
                <div id="tab-avo" class="train-content">
                    <div class="train-input-row">
                        <input type="text" id="avo-input" maxlength="4" placeholder="Préfixe (ex. DEC)" value="DEC">
                        <button onclick="searchAvo()">Tester</button>
                    </div>
                    <div id="avo-results" class="train-results" style="margin-top: 8px;"></div>
                </div>

                <!-- Onglet Anagrammes -->
                <div id="tab-anagrams" class="train-content">
                    <div class="train-input-row">
                        <input type="text" id="anagrams-input" placeholder="Tirage (ex. TIREUR)" value="TIREUR">
                        <button onclick="searchAnagrams()">Chercher</button>
                    </div>
                    <div id="anagrams-results" class="train-results" style="margin-top: 8px;"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        const BOARD_BONUS = {{BOARD_BONUS}};
        const TILE_VALUES = {{TILE_VALUES}};
        let currentGrid = Array(15).fill(null).map(() => Array(15).fill(null));
        let lastSuggestedMoves = [];

        function initBoard() {
            const container = document.getElementById('board');
            container.innerHTML = '';
            for (let r = 0; r < 15; r++) {
                for (let c = 0; c < 15; c++) {
                    const cell = document.createElement('div');
                    cell.className = 'cell';
                    cell.id = `cell-${r}-${c}`;
                    const bonus = BOARD_BONUS[r][c];
                    if (bonus) {
                        cell.classList.add(bonus);
                        cell.textContent = bonus;
                    } else {
                        cell.classList.add('normal');
                    }
                    cell.onclick = () => onCellClick(r, c);
                    container.appendChild(cell);
                }
            }
            updateBagCount();
        }

        function renderGrid() {
            for (let r = 0; r < 15; r++) {
                for (let c = 0; c < 15; c++) {
                    const cell = document.getElementById(`cell-${r}-${c}`);
                    cell.className = 'cell';
                    const bonus = BOARD_BONUS[r][c];
                    if (bonus) cell.classList.add(bonus);
                    else cell.classList.add('normal');

                    const tile = currentGrid[r][c];
                    if (tile) {
                        cell.classList.add('has-tile');
                        if (tile === tile.toLowerCase()) cell.classList.add('is-joker');
                        const val = (tile === tile.toLowerCase() || tile === '?') ? 0 : (TILE_VALUES[tile.toUpperCase()] || 0);
                        cell.innerHTML = `<span class="tile-letter">${tile.toUpperCase()}</span><span class="tile-value">${val}</span>`;
                    } else {
                        cell.textContent = bonus || '';
                    }
                }
            }
            updateBagCount();
        }

        function onCellClick(r, c) {
            const cur = currentGrid[r][c] || '';
            const res = prompt(`Lettre en (${String.fromCharCode(65+r)}${c+1}) :\\n(Majuscule = normale, Minuscule = joker, Vide = effacer)`, cur);
            if (res !== null) {
                const trimmed = res.trim();
                currentGrid[r][c] = trimmed ? trimmed[0] : null;
                renderGrid();
            }
        }

        function clearBoard() {
            if (confirm("Vider complètement le plateau ?")) {
                currentGrid = Array(15).fill(null).map(() => Array(15).fill(null));
                renderGrid();
                document.getElementById('moves-tbody').innerHTML = '<tr><td colspan="6" style="text-align: center; color: #6b7280;">Plateau vidé.</td></tr>';
            }
        }

        async function solvePosition() {
            const rack = document.getElementById('rack-input').value.trim().toUpperCase();
            if (!rack) return alert("Veuillez saisir un chevalet.");
            document.getElementById('speed-badge').textContent = "Calcul...";

            const t0 = performance.now();
            const res = await fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ grid: currentGrid, rack: rack })
            });
            const data = await res.json();
            const t1 = performance.now();
            document.getElementById('speed-badge').textContent = `${(t1 - t0).toFixed(1)} ms (${data.moves.length} coups)`;

            lastSuggestedMoves = data.moves;
            displayMoves(data.moves);
            updateBagDisplay(data.remaining_tiles, data.total_remaining);
        }

        function displayMoves(moves) {
            const tbody = document.getElementById('moves-tbody');
            tbody.innerHTML = '';
            if (moves.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: #ef4444;">Aucun coup légal trouvé.</td></tr>';
                return;
            }
            moves.slice(0, 20).forEach((m, idx) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td><strong>${m.coord_fisf}</strong></td>
                    <td style="font-weight: 700;">${m.word}</td>
                    <td class="score-pill">+${m.score}</td>
                    <td style="color: #9ca3af;">${m.leave || '—'}</td>
                    <td class="equity-pill">${m.equity > 0 ? '+' : ''}${m.equity}</td>
                    <td><button style="padding: 2px 8px; font-size: 0.75rem;" onclick="playMove(${idx})">Jouer</button></td>
                `;
                tr.onmouseenter = () => previewMove(m);
                tr.onmouseleave = () => clearPreview();
                tr.onclick = (e) => {
                    if (e.target.tagName !== 'BUTTON') {
                        previewMove(m);
                    }
                };
                tbody.appendChild(tr);
            });
        }

        function previewMove(m) {
            clearPreview();
            const L = m.word.length;
            for (let i = 0; i < L; i++) {
                const r = m.horizontal ? m.row : m.row + i;
                const c = m.horizontal ? m.col + i : m.col;
                const cell = document.getElementById(`cell-${r}-${c}`);
                if (cell && !currentGrid[r][c]) {
                    cell.classList.add('preview-tile');
                    cell.textContent = m.word[i];
                }
            }
        }

        function clearPreview() {
            document.querySelectorAll('.preview-tile').forEach(c => {
                c.classList.remove('preview-tile');
                const parts = c.id.split('-');
                const r = parseInt(parts[1]), col = parseInt(parts[2]);
                c.textContent = currentGrid[r][col] || BOARD_BONUS[r][col] || '';
            });
        }

        function playMove(idx) {
            const m = lastSuggestedMoves[idx];
            if (!m) return;
            const L = m.word.length;
            for (let i = 0; i < L; i++) {
                const r = m.horizontal ? m.row : m.row + i;
                const c = m.horizontal ? m.col + i : m.col;
                if (!currentGrid[r][c]) {
                    currentGrid[r][c] = m.word[i];
                }
            }
            document.getElementById('rack-input').value = m.leave;
            renderGrid();
            solvePosition();
        }

        function applyTopMove() {
            if (lastSuggestedMoves.length > 0) playMove(0);
        }

        function updateBagCount() {
            fetch('/api/solve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ grid: currentGrid, rack: document.getElementById('rack-input').value })
            }).then(r => r.json()).then(data => {
                updateBagDisplay(data.remaining_tiles, data.total_remaining);
            }).catch(() => {});
        }

        function updateBagDisplay(remMap, total) {
            const countEl = document.getElementById('unseen-count') || document.getElementById('total-bag-count');
            if (countEl) countEl.textContent = total;
            const container = document.getElementById('bag-grid');
            container.innerHTML = '';
            for (const [ch, cnt] of Object.entries(remMap)) {
                const item = document.createElement('div');
                item.className = 'bag-item' + (cnt === 0 ? ' empty' : '');
                item.innerHTML = `<div>${ch}</div><div class="bag-count">${cnt}</div>`;
                container.appendChild(item);
            }
        }

        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.train-content').forEach(c => c.classList.remove('active'));
            const btn = Array.from(document.querySelectorAll('.tab-btn')).find(b => b.getAttribute('onclick').includes(tab));
            if (btn) btn.classList.add('active');
            const target = document.getElementById(`tab-${tab}`);
            if (target) target.classList.add('active');
        }

        async function searchAppuis() {
            const rack = document.getElementById('appuis-input').value.trim();
            const res = await fetch('/api/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'appuis_7_plus_1', query: rack })
            });
            const data = await res.json();
            const div = document.getElementById('appuis-results');
            div.innerHTML = '';
            for (const [lettre, mots] of Object.entries(data.appuis || {})) {
                div.innerHTML += `<div style="margin-top:4px; padding: 2px 0;"><strong>+ ${lettre} :</strong> <span style="color:#10b981; margin-left: 4px;">${mots.join(', ')}</span></div>`;
            }
        }

        async function searchBenjamins() {
            const mot = document.getElementById('benjamins-input').value.trim();
            const res = await fetch('/api/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'benjamins', query: mot })
            });
            const data = await res.json();
            const div = document.getElementById('benjamins-results');
            const items = data.benjamins || [];
            if (items.length === 0) {
                div.innerHTML = '<span style="color:#9ca3af;">Aucun benjamin trouvé.</span>';
                return;
            }
            div.innerHTML = `<div class="pill-list">${items.map(w => `<span class="pill tag">${w}</span>`).join(' ')}</div>`;
        }

        async function searchAvo() {
            const prefix = document.getElementById('avo-input').value.trim();
            const res = await fetch('/api/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'avo', query: prefix })
            });
            const data = await res.json();
            const div = document.getElementById('avo-results');
            const samples = data.samples || [];
            div.innerHTML = `<div style="margin-bottom: 6px;">Total prolongements: <strong>${data.total || 0}</strong></div><div class="pill-list">${samples.map(w => `<span class="pill tag">${w}</span>`).join(' ')}</div>`;
        }

        async function searchAnagrams() {
            const tirage = document.getElementById('anagrams-input').value.trim();
            const res = await fetch('/api/train', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mode: 'anagrams', query: tirage })
            });
            const data = await res.json();
            const div = document.getElementById('anagrams-results');
            const anags = data.anagrams || [];
            if (anags.length === 0) {
                div.innerHTML = '<span style="color:#9ca3af;">Aucune anagramme trouvée.</span>';
                return;
            }
            div.innerHTML = `<div class="pill-list">${anags.map(w => `<span class="pill tag">${w}</span>`).join(' ')}</div>`;
        }

        window.onload = initBoard;
    </script>
</body>
</html>
"""

class ScrabbleHTTPHandler(BaseHTTPRequestHandler):
    """Handler HTTP REST JSON et application Web intégrée."""

    def do_GET(self) -> None:
        if self.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if self.path == "/" or self.path.startswith("/index"):
            bonus_json = json.dumps(BOARD_BONUS)
            tile_values_json = json.dumps(TILE_VALUES)
            html = HTML_PAGE.replace("{{BOARD_BONUS}}", bonus_json).replace("{{TILE_VALUES}}", tile_values_json)
            encoded = html.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)
        else:
            self.send_error(404, "Page introuvable")

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        try:
            payload = json.loads(body)
        except Exception:
            self.send_error(400, "Payload JSON invalide")
            return

        dict_obj, gen = get_shared_engine()

        if self.path == "/api/solve":
            grid_data = payload.get("grid")
            rack = payload.get("rack", "").strip().upper()
            opp_rack = payload.get("opp_rack")
            board = Board.from_dict(grid_data) if grid_data else Board()

            # Stratégiste pour scorer l'équité
            strat = EnzoStrategist(dict_obj, gen)
            moves = gen.generate_all_moves(board, rack)
            bag_count = board.total_remaining_tiles(rack)

            # Évaluer chaque coup avec EnzoStrategist
            moves_out = []
            for m in moves[:50]:
                lv = evaluate_leave(m.leave)
                dp = evaluate_defense_penalty(board, m, bag_count)
                eq = round(m.score + lv - dp, 2)
                moves_out.append({
                    "word": m.word,
                    "row": m.row,
                    "col": m.col,
                    "horizontal": m.horizontal,
                    "coord_fisf": m.coord_fisf,
                    "score": m.score,
                    "tiles_placed": m.tiles_placed,
                    "leave": m.leave,
                    "leave_value": lv,
                    "defense_penalty": dp,
                    "equity": eq,
                    "cross_words": m.cross_words,
                })

            # Trier par équité décroissante (EnzoStrategist)
            moves_out.sort(key=lambda item: item["equity"], reverse=True)

            rem_tiles = board.remaining_tiles(rack)
            response_data = {
                "moves": moves_out,
                "remaining_tiles": rem_tiles,
                "total_remaining": sum(rem_tiles.values()),
                "is_endgame": (sum(rem_tiles.values()) == 0),
            }
            self._send_json(response_data)

        elif self.path == "/api/train":
            mode = payload.get("mode")
            query = payload.get("query", "").strip().upper()

            if mode == "appuis_7_plus_1":
                appuis = dict_obj.find_appuis_7_plus_1(query)
                self._send_json({"appuis": appuis})
            elif mode == "benjamins":
                benjamins = dict_obj.find_benjamins(query)
                self._send_json({"benjamins": benjamins})
            elif mode == "avo":
                exts = dict_obj.find_prefix_extensions(query, min_len=len(query) + 1, max_len=15)
                self._send_json({"total": len(exts), "samples": exts[:40]})
            elif mode == "anagrams":
                anags = dict_obj.find_anagrams(query)
                self._send_json({"anagrams": anags})
            else:
                self.send_error(400, "Mode d'entraînement inconnu")
        else:
            self.send_error(404, "Endpoint API inconnu")

    def _send_json(self, data: Any) -> None:
        encoded = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format, *args):
        # Désactiver les logs verbeux en console
        pass


def run_server(host: str = "127.0.0.1", port: int = 8765) -> None:
    """Démarre le serveur HTTP local."""
    print(f"Chargement initial du moteur Scrabble Enzo...")
    get_shared_engine()
    server = HTTPServer((host, port), ScrabbleHTTPHandler)
    print(f"Serveur Scrabble Enzo actif sur http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nArrêt du serveur.")
        server.server_close()

if __name__ == "__main__":
    run_server()
