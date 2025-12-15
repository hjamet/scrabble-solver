#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <iomanip>

#include "game.h"
#include "datamanager.h"
#include "lexiconparameters.h"
#include "alphabetparameters.h"
#include "board.h"
#include "move.h"

using namespace Quackle;
using namespace std;

// Helper subclass to access protected Board::m_letters
class MyBoard : public Board {
public:
    using Board::Board;
    
    // Set a letter directly (forces board to be non-empty)
    void setSquare(int r, int c, Letter l) {
        if (r >= 0 && r < height() && c >= 0 && c < width()) {
            m_letters[r][c] = l;
            m_empty = false;
        }
    }
};

void setupBoard(GamePosition& pos, const string& boardStr, const AlphabetParameters* alpha) {
    // Construct a new board with desired state
    MyBoard newBoard(15, 15);
    newBoard.prepareEmptyBoard();

    // boardStr is 15x15 = 225 chars.
    for (int r = 0; r < 15; ++r) {
        for (int c = 0; c < 15; ++c) {
            char ch = boardStr[r * 15 + c];
            if (ch != '.') {
                string letterStr(1, ch);
                LetterString ls = alpha->encode(letterStr);
                if (ls.length() > 0) {
                     newBoard.setSquare(r, c, ls[0]);
                }
            }
        }
    }
    
    // Set board to position
    pos.setBoard(newBoard);
    // Crucial: Update cross-checks etc.
    // Quackle might need `updateBritishness` or `prepareForAnalysis`?
    // GamePosition::ensureBoardIsPreparedForAnalysis() calls Board::updateBritishness
    pos.ensureBoardIsPreparedForAnalysis();
}

int main() {
    // 1. Initialize Quackle DataManager
    DataManager dm;
    AlphabetParameters* alpha = dm.alphabetParameters();

    // 2. Load Dictionary
    string gaddagPath = "assets/dictionnaries/french.gaddag";
    cout << "Loading dictionary: " << gaddagPath << "..." << endl;
    
    auto tLoadStart = std::chrono::high_resolution_clock::now();
    dm.lexiconParameters()->loadGaddag(gaddagPath);
    auto tLoadEnd = std::chrono::high_resolution_clock::now();
    
    if (!dm.lexiconParameters()->hasGaddag()) {
        cerr << "Failed to load GADDAG." << endl;
        return 1;
    }
    cout << "Dictionary loaded in " 
         << std::chrono::duration_cast<std::chrono::milliseconds>(tLoadEnd - tLoadStart).count() 
         << " ms." << endl;

    // 3. Load Synthetic Positions
    string positionsPath = "assets/benchmarks/synthetic_positions.txt";
    ifstream posFile(positionsPath);
    if (!posFile.is_open()) {
        cerr << "Failed to open positions file: " << positionsPath << endl;
        return 1;
    }

    struct Pos {
        string board;
        string rack;
    };
    vector<Pos> positions;
    string line;
    while (getline(posFile, line)) {
        size_t pipe = line.find('|');
        if (pipe != string::npos) {
            Pos p;
            p.board = line.substr(0, pipe);
            p.board.erase(remove_if(p.board.begin(), p.board.end(), ::isspace), p.board.end());
            p.rack = line.substr(pipe + 1);
            p.rack.erase(remove_if(p.rack.begin(), p.rack.end(), ::isspace), p.rack.end());
            positions.push_back(p);
        }
    }
    posFile.close();
    cout << "Loaded " << positions.size() << " positions." << endl;

    // 4. Run Benchmark
    long long totalTimeUs = 0;
    long long totalMoves = 0;

    cout << "Running Benchmark..." << endl;
    cout << "#    Rack           Moves     Time(us)" << endl;
    cout << "----------------------------------------" << endl;

    // We reuse one Game object to avoid overhead? No, clean state is safer.
    // Actually GamePosition logic is self contained.
    
    for (size_t i = 0; i < positions.size(); ++i) {
        // Create Game (sets up default players: Player 0 and Player 1)
        Game game;
        PlayerList players;
        players.push_back(Player(MARK_UV("P1")));
        players.push_back(Player(MARK_UV("P2")));
        game.setPlayers(players);
        
        // Need to add initial position
        game.addPosition(); 
        
        // Now valid position exists at game.currentPosition()
        GamePosition& pos = game.currentPosition();
        
        // Setup Board
        setupBoard(pos, positions[i].board, alpha);
        
        // Setup Rack
        string rackStr = positions[i].rack;
        LetterString rackLS;
        for (char c : rackStr) {
            string s(1, c);
            if (c == '?' || c == '*') {
                rackLS += QUACKLE_BLANK_MARK;
            } else {
                rackLS += alpha->encode(s);
            }
        }
        
        // Getting mutable player
        // game.setPlayers was called.
        // pos.currentPlayer() returns Player& in our context?
        // Actually pos.currentPlayer() returns Player&.
        // But Player::rack() returns const Rack&.
        // So we must use Player::setRack.
        pos.currentPlayer().setRack(rackLS);

        // Generate
        auto tStart = std::chrono::high_resolution_clock::now();
        
        // Kibitz calls generator
        // pass a large number to get all moves?
        // Or explicitly rely on allPossiblePlays? 
        // kibitz() fills m_moves.
        pos.kibitz(50000); 
        
        const MoveList& moves = pos.moves();
        
        auto tEnd = std::chrono::high_resolution_clock::now();
        long long duration = std::chrono::duration_cast<std::chrono::microseconds>(tEnd - tStart).count();
        
        totalTimeUs += duration;
        totalMoves += moves.size();

        if (i < 20 || duration > 10000) { 
             cout << left << setw(5) << i 
                  << left << setw(15) << rackStr 
                  << left << setw(10) << moves.size() 
                  << left << setw(10) << duration 
                  << endl;
        }
    }
    
    cout << "----------------------------------------" << endl;
    cout << "Total Moves Found: " << totalMoves << endl;
    cout << "Total Time: " << totalTimeUs << " us" << endl;
    cout << "Average Time per Position: " << (double)totalTimeUs / positions.size() << " us" << endl;

    return 0;
}
