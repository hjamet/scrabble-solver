#include "engine.h"
#include <gtest/gtest.h>

// Test suite for Board class
class BoardTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Set up any common test data here
    }
    
    void TearDown() override {
        // Clean up after tests
    }
};

// Test board creation
TEST(BoardTest, BoardCreation) {
    Board board;
    // Board should be created successfully without crashing
    SUCCEED();
}

// Test that center position is empty initially
TEST(BoardTest, CenterPositionEmpty) {
    Board board;
    EXPECT_TRUE(board.isEmpty(7, 7)) << "Center position should be empty initially";
}

// Test bonus board initialization
TEST(BoardTest, CornerBonusInitialization) {
    Board board;
    EXPECT_EQ(board.getBonus(0, 0), Bonus::TripleWord) 
        << "Corner position should have Triple Word bonus";
}

// Test tile placement
TEST(BoardTest, TilePlacement) {
    Board board;
    Tile testTile('A', 1);
    
    board.setTile(7, 7, testTile);
    EXPECT_FALSE(board.isEmpty(7, 7)) << "Position should not be empty after tile placement";
}

// Test tile retrieval
TEST(BoardTest, TileRetrieval) {
    Board board;
    Tile testTile('A', 1);
    
    board.setTile(7, 7, testTile);
    Tile retrievedTile = board.getTile(7, 7);
    
    EXPECT_EQ(retrievedTile.letter, 'A') << "Retrieved tile should have correct letter";
    EXPECT_EQ(retrievedTile.value, 1) << "Retrieved tile should have correct value";
}

// Test multiple tile placements
TEST(BoardTest, MultipleTilePlacements) {
    Board board;
    
    Tile tileA('A', 1);
    Tile tileB('B', 3);
    
    board.setTile(7, 7, tileA);
    board.setTile(8, 7, tileB);
    
    EXPECT_FALSE(board.isEmpty(7, 7)) << "First position should not be empty";
    EXPECT_FALSE(board.isEmpty(8, 7)) << "Second position should not be empty";
    
    Tile retrievedA = board.getTile(7, 7);
    Tile retrievedB = board.getTile(8, 7);
    
    EXPECT_EQ(retrievedA.letter, 'A') << "First tile should be A";
    EXPECT_EQ(retrievedB.letter, 'B') << "Second tile should be B";
}

// Test board boundaries
TEST(BoardTest, BoardBoundaries) {
    Board board;
    
    // Test that positions outside the board are handled properly
    // This assumes your board has bounds checking
    Tile testTile('X', 8);
    
    // Test placing tile at edge positions
    EXPECT_NO_THROW(board.setTile(0, 0, testTile)) << "Should be able to place tile at (0,0)";
    EXPECT_NO_THROW(board.setTile(14, 14, testTile)) << "Should be able to place tile at (14,14)";
}

// Test bonus positions
TEST(BoardTest, BonusPositions) {
    Board board;
    
    // Test various bonus positions (assuming standard Scrabble board layout)
    EXPECT_EQ(board.getBonus(0, 0), Bonus::TripleWord) << "Corner should be triple word";
    EXPECT_EQ(board.getBonus(7, 7), Bonus::None) << "Center should have no bonus";
    
    // Add more bonus position tests as needed
}

// Test suite for Tile class
class TileTest : public ::testing::Test {
protected:
    void SetUp() override {
        // Set up any common test data here
    }
    
    void TearDown() override {
        // Clean up after tests
    }
};

// Test tile creation
TEST(TileTest, TileCreation) {
    Tile tile('A', 1);
    EXPECT_EQ(tile.letter, 'A') << "Tile should have correct letter";
    EXPECT_EQ(tile.value, 1) << "Tile should have correct value";
}

// Test tile with different letters and values
TEST(TileTest, DifferentTileValues) {
    Tile tileQ('Q', 10);
    EXPECT_EQ(tileQ.letter, 'Q') << "Q tile should have correct letter";
    EXPECT_EQ(tileQ.value, 10) << "Q tile should have correct value";
    
    Tile tileBlank(' ', 0);
    EXPECT_EQ(tileBlank.letter, ' ') << "Blank tile should have space letter";
    EXPECT_EQ(tileBlank.value, 0) << "Blank tile should have zero value";
}