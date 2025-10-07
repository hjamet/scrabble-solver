#include "engine.h"

/**
 * Initialize the board with standard Scrabble bonus layout
 */
Board::Board() {
    // Initialize all positions with no bonus
    for (int row = 0; row < 15; row++) {
        for (int col = 0; col < 15; col++) {
            bonus_board[row][col] = Bonus::None;
            tile_board[row][col] = Tile(); // Empty tile
        }
    }
    
    // Set up the standard Scrabble bonus layout
    // Triple Word Score positions (corners and center)
    bonus_board[0][0] = Bonus::TripleWord;
    bonus_board[0][7] = Bonus::TripleWord;
    bonus_board[0][14] = Bonus::TripleWord;
    bonus_board[7][0] = Bonus::TripleWord;
    bonus_board[7][14] = Bonus::TripleWord;
    bonus_board[14][0] = Bonus::TripleWord;
    bonus_board[14][7] = Bonus::TripleWord;
    bonus_board[14][14] = Bonus::TripleWord;
    
    // Double Word Score positions
    bonus_board[1][1] = Bonus::DoubleWord;
    bonus_board[2][2] = Bonus::DoubleWord;
    bonus_board[3][3] = Bonus::DoubleWord;
    bonus_board[4][4] = Bonus::DoubleWord;
    bonus_board[10][10] = Bonus::DoubleWord;
    bonus_board[11][11] = Bonus::DoubleWord;
    bonus_board[12][12] = Bonus::DoubleWord;
    bonus_board[13][13] = Bonus::DoubleWord;
    
    bonus_board[1][13] = Bonus::DoubleWord;
    bonus_board[2][12] = Bonus::DoubleWord;
    bonus_board[3][11] = Bonus::DoubleWord;
    bonus_board[4][10] = Bonus::DoubleWord;
    bonus_board[10][4] = Bonus::DoubleWord;
    bonus_board[11][3] = Bonus::DoubleWord;
    bonus_board[12][2] = Bonus::DoubleWord;
    bonus_board[13][1] = Bonus::DoubleWord;
    
    // Triple Letter Score positions
    bonus_board[1][5] = Bonus::TripleLetter;
    bonus_board[1][9] = Bonus::TripleLetter;
    bonus_board[5][1] = Bonus::TripleLetter;
    bonus_board[5][5] = Bonus::TripleLetter;
    bonus_board[5][9] = Bonus::TripleLetter;
    bonus_board[5][13] = Bonus::TripleLetter;
    bonus_board[9][1] = Bonus::TripleLetter;
    bonus_board[9][5] = Bonus::TripleLetter;
    bonus_board[9][9] = Bonus::TripleLetter;
    bonus_board[9][13] = Bonus::TripleLetter;
    bonus_board[13][5] = Bonus::TripleLetter;
    bonus_board[13][9] = Bonus::TripleLetter;
    
    // Double Letter Score positions
    bonus_board[0][3] = Bonus::DoubleLetter;
    bonus_board[0][11] = Bonus::DoubleLetter;
    bonus_board[2][6] = Bonus::DoubleLetter;
    bonus_board[2][8] = Bonus::DoubleLetter;
    bonus_board[3][0] = Bonus::DoubleLetter;
    bonus_board[3][7] = Bonus::DoubleLetter;
    bonus_board[3][14] = Bonus::DoubleLetter;
    bonus_board[6][2] = Bonus::DoubleLetter;
    bonus_board[6][6] = Bonus::DoubleLetter;
    bonus_board[6][8] = Bonus::DoubleLetter;
    bonus_board[6][12] = Bonus::DoubleLetter;
    bonus_board[7][3] = Bonus::DoubleLetter;
    bonus_board[7][11] = Bonus::DoubleLetter;
    bonus_board[8][2] = Bonus::DoubleLetter;
    bonus_board[8][6] = Bonus::DoubleLetter;
    bonus_board[8][8] = Bonus::DoubleLetter;
    bonus_board[8][12] = Bonus::DoubleLetter;
    bonus_board[11][0] = Bonus::DoubleLetter;
    bonus_board[11][7] = Bonus::DoubleLetter;
    bonus_board[11][14] = Bonus::DoubleLetter;
    bonus_board[12][6] = Bonus::DoubleLetter;
    bonus_board[12][8] = Bonus::DoubleLetter;
    bonus_board[14][3] = Bonus::DoubleLetter;
    bonus_board[14][11] = Bonus::DoubleLetter;
}

/**
 * Get the bonus type at a specific position
 */
Bonus Board::getBonus(int row, int col) const {
    if (row < 0 || row >= 15 || col < 0 || col >= 15) {
        return Bonus::None;
    }
    return bonus_board[row][col];
}

/**
 * Get the tile at a specific position
 */
Tile Board::getTile(int row, int col) const {
    if (row < 0 || row >= 15 || col < 0 || col >= 15) {
        return Tile(); // Return empty tile for invalid positions
    }
    return tile_board[row][col];
}

/**
 * Set a tile at a specific position
 */
void Board::setTile(int row, int col, const Tile& tile) {
    if (row >= 0 && row < 15 && col >= 0 && col < 15) {
        tile_board[row][col] = tile;
    }
}

/**
 * Check if a position is empty
 */
bool Board::isEmpty(int row, int col) const {
    if (row < 0 || row >= 15 || col < 0 || col >= 15) {
        return false; // Invalid positions are considered not empty
    }
    return tile_board[row][col].isEmpty();
}