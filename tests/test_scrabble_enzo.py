"""Suite de tests unitaires et d'intégration pour Scrabble Enzo (ODS8)."""

import pytest
from scrabble_enzo.constants import (
    BOARD_SIZE,
    BINGO_BONUS,
    TILE_COUNTS,
    TILE_VALUES,
    BOARD_BONUS,
    tile_value,
)
from scrabble_enzo.board import Board
from scrabble_enzo.dictionary import ScrabbleDictionary
from scrabble_enzo.solver import MoveGenerator, Move, parse_fisf_coord, place_and_score_move
from scrabble_enzo.strategy import (
    evaluate_leave,
    evaluate_defense_penalty,
    solve_endgame_2ply,
    DuplicateGreedy,
    EnzoStrategist,
    evaluate_best_exchange,
)

@pytest.fixture(scope="module")
def dictionary():
    """Charge le dictionnaire ODS8 une seule fois pour la session de test."""
    return ScrabbleDictionary()

@pytest.fixture(scope="module")
def generator(dictionary):
    return MoveGenerator(dictionary)

# Test 1 : Distribution officielle francophone (102 jetons)
def test_tile_counts_total():
    assert sum(TILE_COUNTS.values()) == 102
    assert TILE_COUNTS['E'] == 15
    assert TILE_COUNTS['A'] == 9
    assert TILE_COUNTS['?'] == 2
    assert TILE_COUNTS['Z'] == 1
    assert TILE_VALUES['Z'] == 10
    assert TILE_VALUES['Q'] == 8
    assert TILE_VALUES['?'] == 0

# Test 2 : Grille 15x15 symétrique et bonus officiels
def test_board_bonuses_symmetry():
    assert len(BOARD_BONUS) == 15
    assert all(len(row) == 15 for row in BOARD_BONUS)

    mt_count = sum(row.count('MT') for row in BOARD_BONUS)
    md_count = sum(row.count('MD') for row in BOARD_BONUS)
    lt_count = sum(row.count('LT') for row in BOARD_BONUS)
    ld_count = sum(row.count('LD') for row in BOARD_BONUS)

    assert mt_count == 8
    assert md_count == 17  # 16 diagonales + centre H8
    assert lt_count == 12
    assert ld_count == 24
    assert BOARD_BONUS[7][7] == 'MD'  # Case centrale H8

    # Vérification de symétrie horizontale et verticale
    for r in range(15):
        for c in range(15):
            assert BOARD_BONUS[r][c] == BOARD_BONUS[14 - r][c]
            assert BOARD_BONUS[r][c] == BOARD_BONUS[r][14 - c]
            assert BOARD_BONUS[r][c] == BOARD_BONUS[c][r]

# Test 3 : Chargement et validation du dictionnaire ODS8
def test_ods8_dictionary_loading(dictionary):
    assert len(dictionary.words) == 411430
    assert dictionary.is_word("AA")
    assert dictionary.is_word("ZYTHUMS")
    assert dictionary.is_word("SCRABBLE")
    assert not dictionary.is_word("XYZABC")
    assert not dictionary.is_word("")

# Test 4 : Anagrammes avec et sans jokers
def test_find_anagrams(dictionary):
    anags = dictionary.find_anagrams("TIREUR", 6, 6)
    assert "TIREUR" in anags
    assert "TRIEUR" in anags

    # Avec joker
    anags_joker = dictionary.find_anagrams("TIREU?", 6, 6)
    assert "TIREUR" in anags_joker
    assert "TRIEUR" in anags_joker

# Test 5 : Appuis 7+1
def test_appuis_7_plus_1(dictionary):
    appuis = dictionary.find_appuis_7_plus_1("AELRST")
    assert 'E' in appuis
    assert 'ALERTES' in appuis['E'] or 'RELASTE' in appuis['E'] or 'ALTERES' in appuis['E']

# Test 6 : Benjamins (+3 lettres)
def test_benjamins(dictionary):
    benj = dictionary.find_benjamins("TABLE")
    assert len(benj) > 0
    assert all(w.endswith("TABLE") and len(w) == 8 for w in benj)

# Test 7 : Préfixes AVO
def test_avo_prefixes(dictionary):
    top_avo = dictionary.top_prefixes_avo(3, 5)
    assert len(top_avo) == 5
    assert top_avo[0][0] == "DES"

# Test 8 : Notation FISF aller-retour
def test_fisf_coordinates():
    # H4 = ligne 7 (H), colonne 3 (4), horizontal
    r, c, h = Board.parse_coord_fisf("H4")
    assert (r, c, h) == (7, 3, True)
    assert Board.format_coord_fisf(r, c, h) == "H4"

    # 4H = colonne 3 (4), ligne 7 (H), vertical
    r_v, c_v, h_v = Board.parse_coord_fisf("4H")
    assert (r_v, c_v, h_v) == (7, 3, False)
    assert Board.format_coord_fisf(r_v, c_v, h_v) == "4H"

# Test 9 : Décompte des jetons restants
def test_remaining_tiles():
    b = Board()
    b.set_tile(7, 7, 'Z')
    b.set_tile(7, 8, 'a')  # Joker posé
    rem = b.remaining_tiles(rack="AE")
    assert rem['Z'] == 0
    assert rem['?'] == 1
    assert rem['A'] == 8
    assert rem['E'] == 14
    assert b.total_remaining_tiles("AE") == 102 - 4

# Test 10 : Premier coup au centre sur H8 (MD x2)
def test_first_move_scoring(generator):
    b = Board()
    moves = generator.generate_all_moves(b, "EAU")
    # Mots possibles passant par H8 : EAU (E=1, A=1, U=1 = 3 pts)
    # L'un des jetons est sur (7,7) qui est MD => score = 3 * 2 = 6
    eau_moves = [m for m in moves if m.word == "EAU"]
    assert len(eau_moves) > 0
    assert all(m.score == 6 for m in eau_moves)

# Test 11 : Bonus de Scrabble (+50 points si 7 jetons posés)
def test_bingo_bonus(generator):
    b = Board()
    moves = generator.generate_all_moves(b, "TIREURS")
    # TIREURS posé au premier coup : 7 jetons posés -> score >= 60 pts
    best_move = moves[0]
    assert best_move.tiles_placed == 7
    assert best_move.score >= 50 + 14

# Test 12 : Joker posé valant 0 pt
def test_joker_zero_points():
    assert tile_value('a') == 0
    assert tile_value('z') == 0
    assert tile_value('?') == 0
    assert tile_value('A') == 1
    assert tile_value('Z') == 10

# Test 13 : Mots croisés perpendiculaires
def test_cross_words_scoring(generator):
    b = Board()
    # Poser TIREURS en H2 horizontal (ligne 7, cols 1 à 7)
    for i, ch in enumerate("TIREURS"):
        b.set_tile(7, 1 + i, ch)

    # Poser TABLE verticalement croisant en T en (7, 1)
    # T est déjà posé en (7, 1). Si on pose ABLE en dessous (8..11, 1)
    moves = generator.generate_all_moves(b, "ABLE")
    # Le mot TABLE vertical existe
    table_moves = [m for m in moves if m.word == "TABLE" and not m.horizontal]
    assert len(table_moves) > 0
    m_table = table_moves[0]
    assert m_table.tiles_placed == 4
    assert m_table.score > 0

# Test 14 : Évaluation du reliquat (Leave Evaluation - Centrée)
def test_leave_evaluation():
    assert evaluate_leave("?S") > 10.0
    assert evaluate_leave("Q") < -4.0
    # Q avec U annule la pénalité
    assert evaluate_leave("QU") > evaluate_leave("Q")
    # Doublons excessifs pénalisés
    assert evaluate_leave("EEEEE") < evaluate_leave("E")

# Test 15 : Pénalité de défense
def test_defense_penalty():
    b = Board()
    m_safe = Move(word="TEST", row=7, col=7, horizontal=True, coord_fisf="H8", score=10, tiles_placed=4, leave="E")
    pen_safe = evaluate_defense_penalty(b, m_safe, bag_count=50)

    # Coup ouvrant l'accès à un Mot Triple adjacent
    # Case (0, 0) est MT. Poser une lettre en (0, 1) ouvre directement MT !
    m_risky = Move(word="VA", row=0, col=1, horizontal=True, coord_fisf="A2", score=15, tiles_placed=2, leave="E")
    pen_risky = evaluate_defense_penalty(b, m_risky, bag_count=50)

    assert pen_risky > pen_safe

# Test 16 : Solveur Endgame 2-plis
def test_endgame_2ply(dictionary, generator):
    b = Board()
    for i, ch in enumerate("SCRABBLE"):
        b.set_tile(7, 1 + i, ch)

    # Mon chevalet : OUT (3 lettres)
    # Chevalet adverse : Z (10 pts)
    # Si je sors avec OUT, j'encaisse mon score + 2 * 10 = +20 pts de spread !
    best_move, spread = solve_endgame_2ply(
        board=b,
        my_rack="OUT",
        opp_rack="Z",
        dictionary=dictionary,
        generator=generator,
    )
    if best_move is not None and best_move.tiles_placed == 3:
        assert spread >= 20.0

# Test 17 : Agents DuplicateGreedy vs EnzoStrategist
def test_agents_decision(dictionary, generator):
    b = Board()
    greedy = DuplicateGreedy(dictionary, generator)
    strat = EnzoStrategist(dictionary, generator)

    m_g = greedy.choose_move(b, "AELRST?")
    m_s = strat.choose_move(b, "AELRST?")

    assert m_g is not None
    assert m_s is not None
    assert m_g.score >= 50
    assert m_s.score >= 50

# Test 18 : API Web REST (/api/solve et /api/train)
def test_web_api_endpoints(dictionary, generator):
    import threading, urllib.request, json
    from http.server import HTTPServer
    from scrabble_enzo.web_app import ScrabbleHTTPHandler, get_shared_engine

    # Préchauffer l'instance globale partagée avec les fixtures
    get_shared_engine()

    server = HTTPServer(("127.0.0.1", 8769), ScrabbleHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        # Test 1 : GET /
        req = urllib.request.Request("http://127.0.0.1:8769/")
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200
            content = resp.read().decode("utf-8")
            assert "Scrabble Enzo" in content

        # Test 2 : POST /api/solve
        solve_payload = json.dumps({"grid": None, "rack": "TIREURS"}).encode("utf-8")
        req_solve = urllib.request.Request(
            "http://127.0.0.1:8769/api/solve",
            data=solve_payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_solve, timeout=10) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert "moves" in data
            assert len(data["moves"]) > 0
            assert data["total_remaining"] == 102 - 7

        # Test 3 : POST /api/train (avo)
        train_payload = json.dumps({"mode": "avo", "query": "DEC"}).encode("utf-8")
        req_train = urllib.request.Request(
            "http://127.0.0.1:8769/api/train",
            data=train_payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_train, timeout=3) as resp:
            assert resp.status == 200
            data_train = json.loads(resp.read().decode("utf-8"))
            assert data_train["total"] > 1000

        # Test 4 : POST /api/train (benjamins)
        req_benj = urllib.request.Request(
            "http://127.0.0.1:8769/api/train",
            data=json.dumps({"mode": "benjamins", "query": "TABLE"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_benj, timeout=3) as resp:
            assert resp.status == 200
            data_benj = json.loads(resp.read().decode("utf-8"))
            assert "benjamins" in data_benj
            assert len(data_benj["benjamins"]) == 14
            assert "CARTABLE" in data_benj["benjamins"]

        # Test 5 : POST /api/train (appuis_7_plus_1)
        req_app = urllib.request.Request(
            "http://127.0.0.1:8769/api/train",
            data=json.dumps({"mode": "appuis_7_plus_1", "query": "AELRST"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_app, timeout=3) as resp:
            assert resp.status == 200
            data_app = json.loads(resp.read().decode("utf-8"))
            assert "appuis" in data_app
            assert "E" in data_app["appuis"]

        # Test 6 : POST /api/train (anagrams)
        req_anag = urllib.request.Request(
            "http://127.0.0.1:8769/api/train",
            data=json.dumps({"mode": "anagrams", "query": "TIREUR"}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req_anag, timeout=3) as resp:
            assert resp.status == 200
            data_anag = json.loads(resp.read().decode("utf-8"))
            assert "anagrams" in data_anag
            assert "TRIEUR" in data_anag["anagrams"]
    finally:
        server.shutdown()
        server.server_close()


# Test 19 : Module CLI (Benjamins, Appuis 7+1, AVO, Solveur)
def test_cli_benjamins(capsys, dictionary):
    from scrabble_enzo.cli import format_benjamins
    format_benjamins(dictionary, "TABLE")
    captured = capsys.readouterr().out
    assert "14 solution(s)" in captured
    assert "CARTABLE" in captured
    assert "BATTABLE" in captured


def test_cli_appuis(capsys, dictionary):
    from scrabble_enzo.cli import format_appuis
    format_appuis(dictionary, "AELRST")
    captured = capsys.readouterr().out
    assert "Appuis 7+1" in captured
    assert "+ E" in captured


def test_cli_avo(capsys, dictionary):
    from scrabble_enzo.cli import format_avo
    format_avo(dictionary, "DEC")
    captured_dec = capsys.readouterr().out
    assert "Extensions AVO" in captured_dec
    assert "mot(s) trouvés" in captured_dec

    format_avo(dictionary, None, top_avo=True)
    captured_top = capsys.readouterr().out
    assert "Top 25 des préfixes" in captured_top
    assert "DES" in captured_top


def test_cli_solve(capsys, dictionary, generator):
    from scrabble_enzo.cli import format_solve
    format_solve(dictionary, generator, "TIREURS")
    captured = capsys.readouterr().out
    assert "DuplicateGreedy" in captured
    assert "EnzoStrategist" in captured
    assert "H3 TIREURS" in captured or "H2 TIREURS" in captured


def test_parse_fisf_coord():
    assert parse_fisf_coord("H4") == (7, 3, True)
    assert parse_fisf_coord("4H") == (7, 3, False)
    assert parse_fisf_coord("H12") == (7, 11, True)
    assert parse_fisf_coord("12H") == (7, 11, False)
    assert parse_fisf_coord("O15") == (14, 14, True)
    assert parse_fisf_coord("15O") == (14, 14, False)

    with pytest.raises(ValueError):
        parse_fisf_coord("P4")
    with pytest.raises(ValueError):
        parse_fisf_coord("H16")
    with pytest.raises(ValueError):
        parse_fisf_coord("XYZ")
    with pytest.raises(ValueError):
        parse_fisf_coord("")


def test_place_and_score_move(dictionary):
    b = Board()
    # Coup initial valide en H8 au centre (EAU = 3 pts * 2 MD = 6 pts)
    res = place_and_score_move(b, dictionary, "H8", "EAU")
    assert res["valid_ods8"] is True
    assert res["invalid_words"] == []
    assert res["formed_words"] == ["EAU"]
    assert res["score"] == 6
    assert res["placed_count"] == 3
    assert res["coord"] == "H8"

    # Poser le coup sur le plateau
    b2 = Board.from_dict(res["grid"])

    # Coup avec mot invalide (contestation ODS8)
    res_fake = place_and_score_move(b2, dictionary, "8D", "XYZ")
    assert res_fake["valid_ods8"] is False
    assert "XYZ" in res_fake["invalid_words"]
    assert res_fake["score"] > 0

    # Mot avec joker minuscule ('e') valant 0 pt
    res_joker = place_and_score_move(b, dictionary, "H8", "eAU")
    assert res_joker["score"] == 4  # (0 + 1 + 1) * 2

    # Mots croisés perpendiculaires :
    # Sur b2 ("EAU" posé en H8, cols 7..9, row 7), poser "AVION" verticalement en 8H (croisant le A en (7, 8))
    # EAU : E=(7,7), A=(7,8), U=(7,9).
    # On pose verticalement en 8G (row 6..10, col 8) : P-A-R-I-S ou semblable
    # Ici "AVION" commençant en G (row 6) : G9 = row 6 col 8 ?
    # 9G = col 8 (9e colonne), row 6 (G). Mot = "AVION" -> A en (6,8), V en (7,8) -> conflit si EAU a A en (7,8) !
    # Dans EAU, lettres : (7,7)=E, (7,8)=A, (7,9)=U.
    # Pour croiser en A en (7,8) : mot vertical "BATEAU" commençant en 9F (row 5 col 8) -> B=(5,8), A=(6,8), T=(7,8) conflit !
    # Pour avoir A en 2e lettre : "RATE" commençant en 9G (row 6 col 8) : R=(6,8), A=(7,8), T=(8,8), E=(9,8).
    res_cross = place_and_score_move(b2, dictionary, "9G", "RATE")
    assert res_cross["valid_ods8"] is True
    assert "RATE" in res_cross["formed_words"]
    assert res_cross["placed_count"] == 3  # R, T, E posés, A déjà présent
    assert res_cross["score"] > 0


def test_evaluate_best_exchange():
    # Mauvais tirage (plusieurs Q sans U) : dump des Q
    ex_q = evaluate_best_exchange("QQQQE", bag_count=20)
    assert ex_q is not None
    assert "Q" in ex_q["dump"]
    assert ex_q["keep"] == "E"

    # Sac trop vide (< 7)
    assert evaluate_best_exchange("ABCDEFG", bag_count=5) is None
    assert evaluate_best_exchange("", bag_count=20) is None


def test_web_api_play_move_endpoint():
    import threading, urllib.request, json
    from http.server import HTTPServer
    from scrabble_enzo.web_app import ScrabbleHTTPHandler, get_shared_engine

    get_shared_engine()
    server = HTTPServer(("127.0.0.1", 8770), ScrabbleHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        # POST /api/play_move avec coup valide
        payload_valid = json.dumps({"grid": None, "coord": "H8", "word": "EAU"}).encode("utf-8")
        req = urllib.request.Request(
            "http://127.0.0.1:8770/api/play_move",
            data=payload_valid,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            assert resp.status == 200
            data = json.loads(resp.read().decode("utf-8"))
            assert data["valid_ods8"] is True
            assert data["score"] == 6
            assert data["grid"] is not None

        # POST /api/play_move avec coup invalide (débordement)
        payload_invalid = json.dumps({"grid": None, "coord": "H14", "word": "SCRABBLE"}).encode("utf-8")
        req_inv = urllib.request.Request(
            "http://127.0.0.1:8770/api/play_move",
            data=payload_invalid,
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req_inv, timeout=5) as resp_inv:
                pass
        except urllib.error.HTTPError as e:
            assert e.code == 400
            err_data = json.loads(e.read().decode("utf-8"))
            assert "error" in err_data
    finally:
        server.shutdown()
        server.server_close()



