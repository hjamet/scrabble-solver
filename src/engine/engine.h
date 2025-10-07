#ifndef ENGINE_H
#define ENGINE_H

#include <cstdint>

/**
 * Bonus types for special board positions
 */
enum class Bonus {
    None = 0,
    DoubleLetter = 1,
    TripleLetter = 2,
    DoubleWord = 3,
    TripleWord = 4
};

/**
 * Represents a tile on the board
 */
struct Tile {
    char letter;    // The letter (0 for empty, '*' for blank/joker)
    int value;      // Point value of the tile
    
    // Default constructor for empty tile
    Tile() : letter(0), value(0) {}
    
    // Constructor for specific tile
    Tile(char l, int v) : letter(l), value(v) {}
    
    // Check if tile is empty
    bool isEmpty() const { return letter == 0; }
    
    // Check if tile is a blank/joker
    bool isBlank() const { return letter == '*'; }
};

/**
 * Represents a move on the board
 */
struct Move {
    int row;                    // Starting row (0-14)
    int col;                    // Starting column (0-14)
    bool horizontal;            // true for horizontal, false for vertical
    Tile tiles[7];             // Tiles to place (max 7 tiles)
    int tileCount;             // Number of tiles in this move
    
    // Default constructor
    Move() : row(0), col(0), horizontal(true), tileCount(0) {}
};

/**
 * Represents the Scrabble game board
 */
class Board {
private:
    // Static bonus board (read-only after initialization)
    Bonus bonus_board[15][15];
    
    // Dynamic tile board (modified during gameplay)
    Tile tile_board[15][15];

public:
    /**
     * Constructor - initializes the board with standard Scrabble layout
     */
    Board();
    
    /**
     * Get the bonus type at a specific position
     * @param row Row index (0-14)
     * @param col Column index (0-14)
     * @return Bonus type at the position
     */
    Bonus getBonus(int row, int col) const;
    
    /**
     * Get the tile at a specific position
     * @param row Row index (0-14)
     * @param col Column index (0-14)
     * @return Tile at the position
     */
    Tile getTile(int row, int col) const;
    
    /**
     * Set a tile at a specific position
     * @param row Row index (0-14)
     * @param col Column index (0-14)
     * @param tile Tile to place
     */
    void setTile(int row, int col, const Tile& tile);
    
    /**
     * Check if a position is empty
     * @param row Row index (0-14)
     * @param col Column index (0-14)
     * @return true if position is empty
     */
    bool isEmpty(int row, int col) const;
};

#endif /* ENGINE_H */
