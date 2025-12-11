#include "MoveGenerator.h"
#include <iostream>
#include <vector>
#include <cassert>

using namespace Scrabble;

int main() {
    std::cout << "Starting MoveGenerator Test..." << std::endl;

    Board board;
    Gaddag gaddag;
    // We don't necessarily need to load the huge dictionary for a skeleton test
    // But for a real test we would.
    
    MoveGenerator moveGen;
    std::vector<char> rack = {'A', 'B', 'C', 'D', 'E', 'F', 'G'};
    
    std::cout << "Generating moves..." << std::endl;
    std::vector<Move> moves = moveGen.generateMoves(board, rack, gaddag);
    
    std::cout << "Generated " << moves.size() << " moves." << std::endl;
    
    // Since implementation is empty, it should be 0 or throw if we had logic
    // Currently it returns empty vector.
    
    return 0;
}
