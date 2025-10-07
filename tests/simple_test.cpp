#include "engine.h"
#include <iostream>
#include <cassert>

// Simple test functions without Google Test
void testBoardCreation() {
    std::cout << "Testing board creation... ";
    Board board;
    std::cout << "PASSED" << std::endl;
}

void testCenterPositionEmpty() {
    std::cout << "Testing center position is empty... ";
    Board board;
    assert(board.isEmpty(7, 7));
    std::cout << "PASSED" << std::endl;
}

void testCornerBonusInitialization() {
    std::cout << "Testing corner bonus initialization... ";
    Board board;
    assert(board.getBonus(0, 0) == Bonus::TripleWord);
    std::cout << "PASSED" << std::endl;
}

void testTilePlacement() {
    std::cout << "Testing tile placement... ";
    Board board;
    Tile testTile('A', 1);
    
    board.setTile(7, 7, testTile);
    assert(!board.isEmpty(7, 7));
    std::cout << "PASSED" << std::endl;
}

void testTileRetrieval() {
    std::cout << "Testing tile retrieval... ";
    Board board;
    Tile testTile('A', 1);
    
    board.setTile(7, 7, testTile);
    Tile retrievedTile = board.getTile(7, 7);
    
    assert(retrievedTile.letter == 'A');
    assert(retrievedTile.value == 1);
    std::cout << "PASSED" << std::endl;
}

void testMultipleTilePlacements() {
    std::cout << "Testing multiple tile placements... ";
    Board board;
    
    Tile tileA('A', 1);
    Tile tileB('B', 3);
    
    board.setTile(7, 7, tileA);
    board.setTile(8, 7, tileB);
    
    assert(!board.isEmpty(7, 7));
    assert(!board.isEmpty(8, 7));
    
    Tile retrievedA = board.getTile(7, 7);
    Tile retrievedB = board.getTile(8, 7);
    
    assert(retrievedA.letter == 'A');
    assert(retrievedB.letter == 'B');
    std::cout << "PASSED" << std::endl;
}

void testBoardBoundaries() {
    std::cout << "Testing board boundaries... ";
    Board board;
    Tile testTile('X', 8);
    
    // Test placing tile at edge positions
    board.setTile(0, 0, testTile);
    board.setTile(14, 14, testTile);
    
    assert(!board.isEmpty(0, 0));
    assert(!board.isEmpty(14, 14));
    std::cout << "PASSED" << std::endl;
}

void testBonusPositions() {
    std::cout << "Testing bonus positions... ";
    Board board;
    
    assert(board.getBonus(0, 0) == Bonus::TripleWord);
    assert(board.getBonus(7, 7) == Bonus::None);
    std::cout << "PASSED" << std::endl;
}

void testTileCreation() {
    std::cout << "Testing tile creation... ";
    Tile tile('A', 1);
    assert(tile.letter == 'A');
    assert(tile.value == 1);
    std::cout << "PASSED" << std::endl;
}

void testDifferentTileValues() {
    std::cout << "Testing different tile values... ";
    Tile tileQ('Q', 10);
    assert(tileQ.letter == 'Q');
    assert(tileQ.value == 10);
    
    Tile tileBlank(' ', 0);
    assert(tileBlank.letter == ' ');
    assert(tileBlank.value == 0);
    std::cout << "PASSED" << std::endl;
}

int main() {
    std::cout << "Running Scrabble Engine Tests..." << std::endl;
    std::cout << "=================================" << std::endl;
    
    try {
        testBoardCreation();
        testCenterPositionEmpty();
        testCornerBonusInitialization();
        testTilePlacement();
        testTileRetrieval();
        testMultipleTilePlacements();
        testBoardBoundaries();
        testBonusPositions();
        testTileCreation();
        testDifferentTileValues();
        
        std::cout << "=================================" << std::endl;
        std::cout << "All tests PASSED!" << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cout << "=================================" << std::endl;
        std::cout << "Test FAILED: " << e.what() << std::endl;
        return 1;
    } catch (...) {
        std::cout << "=================================" << std::endl;
        std::cout << "Test FAILED: Unknown error" << std::endl;
        return 1;
    }
}
