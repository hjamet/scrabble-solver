#include "engine.h"

/**
 * Initialize the board with standard Scrabble bonus layout
 */
Board::Board() {
    // Initialize all positions with no bonus and empty tile
    for (int row = 0; row < 15; row++) {
        for (int col = 0; col < 15; col++) {
            bonus_board[row][col] = Bonus::None;
            tile_board[row][col] = Tile();
        }
    }

    // Triple Word Score: corners and center edges (diagonals at 0,0; 0,7; 0,14; 7,0; 7,14; 14,0; 14,7; 14,14)
    for (int i = 0; i < 15; i++) {
        if (i == 0 || i == 7 || i == 14) {
            bonus_board[0][i] = Bonus::TripleWord;
            bonus_board[14][i] = Bonus::TripleWord;
            bonus_board[i][0] = Bonus::TripleWord;
            bonus_board[i][14] = Bonus::TripleWord;
        }
    }

    // Double Word Score: main diagonals except corners and center
    for (int i = 1; i < 14; i++) {
        if (i != 7) {
            bonus_board[i][i] = Bonus::DoubleWord;
            bonus_board[i][14 - i] = Bonus::DoubleWord;
        }
    }

    // Triple Letter Score: 12 positions, symmetric
    int triple_letter_coords[12][2] = {
        {1,5},{1,9},{5,1},{5,5},{5,9},{5,13},
        {9,1},{9,5},{9,9},{9,13},{13,5},{13,9}
    };
    for (int i = 0; i < 12; i++) {
        int r = triple_letter_coords[i][0];
        int c = triple_letter_coords[i][1];
        bonus_board[r][c] = Bonus::TripleLetter;
    }

    // Double Letter Score: pattern-based, but not fully regular, so use list
    int double_letter_coords[24][2] = {
        {0,3},{0,11},{2,6},{2,8},{3,0},{3,7},{3,14},
        {6,2},{6,6},{6,8},{6,12},{7,3},{7,11},
        {8,2},{8,6},{8,8},{8,12},{11,0},{11,7},{11,14},
        {12,6},{12,8},{14,3},{14,11}
    };
    for (int i = 0; i < 24; i++) {
        int r = double_letter_coords[i][0];
        int c = double_letter_coords[i][1];
        bonus_board[r][c] = Bonus::DoubleLetter;
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