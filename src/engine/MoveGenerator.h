#ifndef MOVE_GENERATOR_H
#define MOVE_GENERATOR_H

#include "engine.h"
#include "Gaddag.h"
#include <vector>
#include <string>
#include <cstdint>

namespace Scrabble {

    class MoveGenerator {
    private:
        // Helper to check if a square is an anchor
        bool isAnchor(const Board& board, int row, int col) const;
        
        // Helper to compute cross-checks (bitmask of valid letters for each square)
        // Returns a 15x15 array where each entry is a bitmask (1 << (letter - 'A'))
        // 0x3FFFFFF means all letters allowed.
        void computeCrossChecks(const Board& board, const Gaddag& gaddag, uint32_t crossChecks[15][15]) const;

        // Recursive generation function (Rightwards / Standard GoOn)
        void gen(int row, int col, std::string word, const std::vector<char>& rack, 
                 Node* arc, Node* oldArc, int direction, 
                 const Board& board, const uint32_t crossChecks[15][15], 
                 std::vector<Move>& moves) const;

        // Recursive generation function (Leftwards for GADDAG)
        void genLeft(int row, int col, std::string prefix, const std::vector<char>& rack, 
                 Node* arc, int anchorRow, int anchorCol,
                 const Board& board, const uint32_t crossChecks[15][15], 
                 std::vector<Move>& moves) const;

        // Add a valid move to the list
        void recordMove(const Board& board, int row, int col, const std::string& word, bool horizontal, std::vector<Move>& moves) const;

    public:
        MoveGenerator();
        ~MoveGenerator();

        /**
         * Generate all legal moves for a given board and rack.
         * @param board The current game board.
         * @param rack The player's current rack (e.g. "ABCDEFG").
         * @param gaddag The dictionary.
         * @return A vector of valid moves.
         */
        std::vector<Move> generateMoves(const Board& board, const std::vector<char>& rack, const Gaddag& gaddag) const;
    };

}

#endif // MOVE_GENERATOR_H
