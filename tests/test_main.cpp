#include "engine.h"
#include <stdio.h>

int main(void) {
    printf("Testing Scrabble Engine...\n");
    
    /* Test Board creation */
    Board board;
    printf("✓ Board creation successful\n");
    
    /* Test basic board functionality */
    // Test that center position is empty initially
    if (board.isEmpty(7, 7)) {
        printf("✓ Center position is empty as expected\n");
    } else {
        printf("ERROR: Center position should be empty\n");
        return 1;
    }
    
    // Test bonus board initialization
    if (board.getBonus(0, 0) == Bonus::TripleWord) {
        printf("✓ Corner position has correct bonus (Triple Word)\n");
    } else {
        printf("ERROR: Corner position should have Triple Word bonus\n");
        return 1;
    }
    
    // Test tile placement
    Tile testTile('A', 1);
    board.setTile(7, 7, testTile);
    if (!board.isEmpty(7, 7)) {
        printf("✓ Tile placement successful\n");
    } else {
        printf("ERROR: Tile placement failed\n");
        return 1;
    }
    
    // Test tile retrieval
    Tile retrievedTile = board.getTile(7, 7);
    if (retrievedTile.letter == 'A' && retrievedTile.value == 1) {
        printf("✓ Tile retrieval successful\n");
    } else {
        printf("ERROR: Tile retrieval failed\n");
        return 1;
    }
    
    printf("All tests passed!\n");
    return 0;
}
