#include "MoveGenerator.h"
#include <algorithm>
#include <iostream>

namespace Scrabble {

    MoveGenerator::MoveGenerator() {}
    MoveGenerator::~MoveGenerator() {}

    bool MoveGenerator::isAnchor(const Board& board, int row, int col) const {
        if (!board.isEmpty(row, col)) return false;

        // Check limits
        if (row < 0 || row >= 15 || col < 0 || col >= 15) return false;

        // Check if adjacent to a filled square
        bool hasNeighbor = false;
        if (row > 0 && !board.isEmpty(row - 1, col)) hasNeighbor = true;
        if (row < 14 && !board.isEmpty(row + 1, col)) hasNeighbor = true;
        if (col > 0 && !board.isEmpty(row, col - 1)) hasNeighbor = true;
        if (col < 14 && !board.isEmpty(row, col + 1)) hasNeighbor = true;

        if (hasNeighbor) return true;

        // Center square is an anchor if board is empty (start of game)
        if (row == 7 && col == 7) {
            // Check if board is truly empty (naive check)
            // Ideally we pass a flag 'isFirstMove', but checking center emptiness + neighbors is mostly correct for first move logic
            // Actually, if center is empty, it MUST be the first move or a subsequent move connecting through it,
            // but standard rules say first move MUST cover center.
            return true;
        }

        return false;
    }

    // Check if placing 'letter' at (row, col) forms valid cross-words
    // This is a naive implementation using checks for neighbors.
    // In efficient engines, this is pre-computed.
    bool checkCrossWord(const Board& board, const Gaddag& gaddag, int row, int col, char letter) {
        // Construct vertical word
        std::string word = "";
        word += letter;

        // Scan up
        int r = row - 1;
        while (r >= 0 && !board.isEmpty(r, col)) {
            word.insert(0, 1, board.getTile(r, col).letter);
            r--;
        }
        
        // Scan down
        r = row + 1;
        while (r < 15 && !board.isEmpty(r, col)) {
            word += board.getTile(r, col).letter;
            r++;
        }

        if (word.length() == 1) return true; // No cross-word formed
        return gaddag.contains(word);
    }

    void MoveGenerator::computeCrossChecks(const Board& board, const Gaddag& gaddag, uint32_t crossChecks[15][15]) const {
        for(int i=0; i<15; ++i) {
            for(int j=0; j<15; ++j) {
                crossChecks[i][j] = 0;
                
                // If the square is occupied, cross-check is irrelevant (or full mask)
                if (!board.isEmpty(i, j)) {
                    crossChecks[i][j] = 0x3FFFFFF; 
                    continue;
                }

                // Try all letters A-Z
                for (char c = 'A'; c <= 'Z'; ++c) {
                     if (checkCrossWord(board, gaddag, i, j, c)) {
                         crossChecks[i][j] |= (1 << (c - 'A'));
                     }
                }
                
                // Optimization: if no vertical neighbors, allow all (word length 1 is always valid technically in cross check context, unless board isolated)
                // My checkCrossWord returns true for len 1.
                // So if isolated, loop sets all bits.
            }
        }
    }

    std::vector<Move> MoveGenerator::generateMoves(const Board& board, const std::vector<char>& rack, const Gaddag& gaddag) const {
        std::vector<Move> moves;
        uint32_t crossChecks[15][15];
        computeCrossChecks(board, gaddag, crossChecks);

        Node* root = gaddag.getRoot();
        
        // Horizontal Pass
        for (int r = 0; r < 15; ++r) {
            for (int c = 0; c < 15; ++c) {
                if (isAnchor(board, r, c)) {
                    // Start generation with (r,c) as the "Pivot" (L1 in GADDAG path)
                    // We place/match a letter at (r, c).
                    // This covers ALL words because every word has at least one letter, and every letter can be a pivot.
                    // (Actually GADDAG ensures every word has a pivot L1).
                    
                    // We call genLeft starting at (r,c).
                    // genLeft will:
                    // 1. Try to place/match a letter at curr_col.
                    // 2. If successful, check if Pivot formed (Arc->Delimiter calls genRight).
                    // 3. Recurse Left.
                    
                    genLeft(r, c, "", rack, root, r, c, board, crossChecks, moves);
                }
            }
        }
        return moves;
    }

    void MoveGenerator::genLeft(int row, int col, std::string prefix, const std::vector<char>& rack, 
                            Node* arc, int anchorRow, int anchorCol,
                            const Board& board, const uint32_t crossChecks[15][15], 
                            std::vector<Move>& moves) const {
        
        if (col < 0) return; // Board edge

        // Helper lambda to process a letter L at (row, col)
        auto processLetter = [&](char L, Node* nextArc, const std::vector<char>& nextRack) {
            // New Prefix: append L to "prefix" (which stores the word fragment reversed? No, let's store it normal sequence for simplicity?)
            // But GADDAG traversal is L1 -> L2 -> L3. Word is ...L3 L2 L1.
            // So if we traverse C->A. Word is ...AC.
            // Effectively we present letters in Reverse order to `gen` (Right).
            // `prefix` here will accumulate the "GADDAG Path Letters".
            // So if path is C->A. `prefix` = "CA".
            // When we switch to Right, we reverse it: "AC".
            
            std::string newPrefix = prefix + L;
            
            // 1. Check for Delimiter (Pivot Point)
            // If the arc has a delimiter, it means the sequence we just traced (L...L1) is a valid Prefix.
            // The Split point is AFTER (row, col) (to the right).
            // i.e. Suffix starts at col + 1 ?
            // NO. The Anchor of generation was `anchorCol`.
            // We started at `anchorCol`. We are now at `col` (<= anchorCol).
            // The split is always immediately to the right of the INITIAL Pivot?
            // No. The split is immediately to the right of the CURRENT letter being placed?
            // GADDAG: L1 L2 .. D R1 ..
            // We correspond to L1, L2...
            // Wait.
            // Path: C -> D -> ... (Word C...)
            // Path: A -> C -> D -> ... (Word CA...)
            // So the Delimiter is ALWAYS reached after processing the Left Part.
            // And the Right Part starts immediately to the right of the L1 (The FIRST letter of path).
            // L1 is at `anchorCol`.
            // So Right Part starts at `anchorCol + 1`.
            
            if (nextArc->children.count(GADDAG_DELIMITER)) {
                 Node* rightStartArc = nextArc->children[GADDAG_DELIMITER];
                 std::string wordSoFar = newPrefix;
                 std::reverse(wordSoFar.begin(), wordSoFar.end());
                 
                 // We must check if we are ALLOWED to stop going left.
                 // We can only stop going left if the square to the left (col-1) is empty!
                 // If (col-1) is occupied, we MUST include it in the word.
                 if (col == 0 || board.isEmpty(row, col - 1)) {
                      gen(row, anchorCol + 1, wordSoFar, nextRack, rightStartArc, nextArc, 0, board, crossChecks, moves);
                 }
            }
            
            // 2. Recurse Left
            // Only if we can (col > 0) AND we are not blocked?
            // Actually standard limits apply.
            // But if (col-1) is empty, we consume rack.
            // If (col-1) occupied, we match.
            // Optimization: If we just placed a tile on Anchor, we can go left.
            // If we are left of anchor, we continue.
            genLeft(row, col - 1, newPrefix, nextRack, nextArc, anchorRow, anchorCol, board, crossChecks, moves);
        };

        if (board.isEmpty(row, col)) {
            // Try all letters in rack
             for (size_t i = 0; i < rack.size(); ++i) {
                char rackTile = rack[i];
                std::vector<char> nextRack = rack;
                nextRack.erase(nextRack.begin() + i);

                auto tryChar = [&](char C) {
                    if (arc->children.count(C)) {
                        if (crossChecks[row][col] & (1 << (C - 'A'))) {
                             processLetter(C, arc->children[C], nextRack);
                        }
                    }
                };

                if (rackTile == '?' || rackTile == '*') {
                    for (char c = 'A'; c <= 'Z'; ++c) tryChar(c);
                } else {
                    tryChar(rackTile);
                }
             }
        } else {
            // Occupied
            char L = board.getTile(row, col).letter;
            if (arc->children.count(L)) {
                 processLetter(L, arc->children[L], rack);
            }
        }
    }

    void MoveGenerator::gen(int row, int col, std::string word, const std::vector<char>& rack, 
                            Node* arc, Node* oldArc, int direction, 
                            const Board& board, const uint32_t crossChecks[15][15], 
                            std::vector<Move>& moves) const {
        
        // 1. Record Move if valid
        // Condition: Arc is terminal AND square is not occupied (or we are at end of board)
        // Wait, standard moves can end anywhere if terminal.
        // BUT if square (row, col) is occupied, we MUST incorporate it. We cannot stop.
        // So we record ONLY if (col >= 15 OR board.isEmpty(row, col)).
        
        if (col >= 15 || board.isEmpty(row, col)) {
            if (arc->isTerminal) {
                recordMove(board, row, col, word, true, moves);
            }
        }
        
        if (col >= 15) return;

        auto processLetter = [&](char L, Node* nextArc, const std::vector<char>& nextRack) {
             gen(row, col + 1, word + L, nextRack, nextArc, arc, direction, board, crossChecks, moves);
        };

        if (board.isEmpty(row, col)) {
            for (size_t i = 0; i < rack.size(); ++i) {
                char rackTile = rack[i];
                std::vector<char> nextRack = rack;
                nextRack.erase(nextRack.begin() + i);
                
                auto tryChar = [&](char C) {
                    if (arc->children.count(C)) {
                        if (crossChecks[row][col] & (1 << (C - 'A'))) {
                             processLetter(C, arc->children[C], nextRack);
                        }
                    }
                };

                if (rackTile == '?' || rackTile == '*') {
                    for (char c = 'A'; c <= 'Z'; ++c) tryChar(c);
                } else {
                    tryChar(rackTile);
                }
            }
        } else {
            char L = board.getTile(row, col).letter;
            if (arc->children.count(L)) {
                 processLetter(L, arc->children[L], rack);
            }
        }
    }

    void MoveGenerator::recordMove(const Board& board, int row, int col, const std::string& word, bool horizontal, std::vector<Move>& moves) const {
        // 'col' is the position *after* the last letter.
        int startCol = col - word.length();
        
        // Validation: Must have placed at least one tile.
        bool placed = false;
        int tileCount = 0;
        Move m;
        m.row = row;
        m.col = startCol;
        m.horizontal = horizontal;
        m.word = word;
        m.score = 0; 
        
        for (int i = 0; i < word.length(); ++i) {
            if (board.isEmpty(row, startCol + i)) {
                placed = true;
                // Simplified: Assuming 1pt for now as placeholder for real tile score lookups
                m.tiles[tileCount++] = Tile(word[i], 1); 
            }
        }
        m.tileCount = tileCount;

        if (placed) {
            moves.push_back(m);
        }
    }

}
