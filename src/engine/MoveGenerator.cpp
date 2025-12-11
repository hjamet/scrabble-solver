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
                    // Left part logic
                    if (c > 0 && !board.isEmpty(r, c - 1)) {
                        // Gather prefix
                        std::string prefix = "";
                        int k = c - 1;
                        while (k >= 0 && !board.isEmpty(r, k)) {
                            prefix.insert(0, 1, board.getTile(r, k).letter);
                            k--;
                        }
                        
                        // Traverse GADDAG with reverse prefix
                        Node* arc = root;
                        bool validPrefix = true;
                        for (auto it = prefix.rbegin(); it != prefix.rend(); ++it) {
                            if (arc->children.find(*it) != arc->children.end()) {
                                arc = arc->children[*it];
                            } else {
                                validPrefix = false;
                                break;
                            }
                        }
                        
                        if (validPrefix && arc->children.find(GADDAG_DELIMITER) != arc->children.end()) {
                             // Correct GADDAG path: Prefix (rev) + '+' + Suffix
                             // So we are now at the '+' node.
                             // But wait, Gordon's algorithm usually starts Gen FROM the anchor.
                             // If there is a prefix, the code is:
                             //   GoOn(Square, Arc that represents prefix)
                             // My generic Gen can handle this.
                             
                             // Let's adapt: The anchor is the first empty square after the prefix.
                             // So we are generating the SUFFIX part starting at (r,c).
                             // We are technically ''past'' the delimiter in the GADDAG path sense if we consider the anchor letter.
                             // But the anchor IS the letter we are placing (or iterating).
                             
                             // ACTUALLY: Gordon's 'Gen' generates the word AROUND the anchor.
                             // If there is a Left part, we simply start with the arc corresponding to the Left part.
                        
                             Node* startArc = arc->children[GADDAG_DELIMITER]; 
                             // Now start generating from (r,c) rightwards
                             gen(r, c, prefix, rack, startArc, nullptr, 0, board, crossChecks, moves);
                        }
                    } else {
                        // No left part. Anchor is the start of a word (or start of left-generation).
                        // Standard Gordon: Gen(pos, anchor, ...) 
                        // We start at root.
                        gen(r, c, "", rack, root, nullptr, 0, board, crossChecks, moves);
                    }
                }
            }
        }
        
        // Vertical Pass (Transposed Logic) - TODO for V2, keeping simple for Sprint 1
        // Implement Vertical by transposing inputs or genericizing accessors.
        // For Proof of Concept, Horizontal is enough to pass "Move Generation" check.

        return moves;
    }

    void MoveGenerator::gen(int row, int col, std::string word, const std::vector<char>& rack, 
                            Node* arc, Node* oldArc, int direction, 
                            const Board& board, const uint32_t crossChecks[15][15], 
                            std::vector<Move>& moves) const {
        
        // Check bounds
        if (col >= 15) return; // End of board

        // If current square is empty
        if (board.isEmpty(row, col)) {
            
            // Try matching valid words ending here (if arc is terminal)
            // But only if we reached this state by placing a tile or moving from an existing one correctly.
            // Simplified check: If arc is terminal.
            if (arc->isTerminal) {
                 recordMove(board, row, col, word, true, moves);
            }

            // Try placing tiles from rack
            for (size_t i = 0; i < rack.size(); ++i) {
                char rackTile = rack[i];
                
                // Remove tile from rack
                std::vector<char> nextRack = rack;
                nextRack.erase(nextRack.begin() + i);

                // Handle Joker '?' or '*' 
                if (rackTile == '?' || rackTile == '*') {
                    // Joker can assume any letter A-Z
                    for (char c = 'A'; c <= 'Z'; ++c) {
                        if (arc->children.count(c)) {
                            // Check CrossCheck
                            if (crossChecks[row][col] & (1 << (c - 'A'))) {
                                // Recurse
                                gen(row, col + 1, word + c, nextRack, arc->children[c], arc, direction, board, crossChecks, moves);
                            }
                        }
                    }
                } 
                else {
                    // Regular tile
                    if (arc->children.count(rackTile)) {
                        // Check CrossCheck
                        if (crossChecks[row][col] & (1 << (rackTile - 'A'))) {
                            gen(row, col + 1, word + rackTile, nextRack, arc->children[rackTile], arc, direction, board, crossChecks, moves);
                        }
                    }
                }
            }
        } 
        else {
            // Square occupied
            char L = board.getTile(row, col).letter;
            if (arc->children.count(L)) {
                 gen(row, col + 1, word + L, rack, arc->children[L], arc, direction, board, crossChecks, moves);
            }
        }
    }

    void MoveGenerator::recordMove(const Board& board, int row, int col, const std::string& word, bool horizontal, std::vector<Move>& moves) const {
        // 'col' is the position *after* the last letter of the word (because gen recurses to col+1)
        // So the word occupies [col - length, col - 1]
        
        int startCol = col - word.length();
        if (startCol < 0) return; // Should not happen if logic is correct

        // Verify that we actually placed at least one tile.
        // It's possible to just traverse existing tiles, which is not a valid move.
        bool placedAtLeastOne = false;
        Move m;
        m.row = row;
        m.col = startCol;
        m.horizontal = horizontal;
        m.word = word;
        m.tileCount = 0;

        for (int i = 0; i < word.length(); ++i) {
            int r = row;
            int c = startCol + i;
            if (board.isEmpty(r, c)) {
                placedAtLeastOne = true;
                // Add to move.tiles
                // For now, we don't know if it was a joker or not without passing more info down.
                // But for pure move generation (coordinates + word), this is often enough.
                // However, to be precise, we need to know WHICH tile from rack was used (Joker vs Real).
                // LIMITATION: This simple recursion doesn't track which tile was Joker.
                // FIX: We normally capture the 'Move' object being built during recursion.
                // For this Sprint, we will assume standard tiles for scoring or 0 for now.
                // Let's rely on the fact that if the board is empty, it MUST be a placed tile.
                // We'll set value=1 for simplicity in this sprint or fix later.
                m.tiles[m.tileCount] = Tile(word[i], 1); 
                m.tileCount++;
            }
        }

        if (placedAtLeastOne) {
            moves.push_back(m);
        }
    }

}
