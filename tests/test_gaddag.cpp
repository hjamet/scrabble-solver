#include "Gaddag.h"
#include <iostream>
#include <cassert>
#include <chrono>

using namespace Scrabble;

int main() {
    std::cout << "Starting GADDAG Test..." << std::endl;

    Gaddag gaddag;
    std::string dictPath = "assets/dictionnaries/french.txt";
    
    // Time the loading
    auto start = std::chrono::high_resolution_clock::now();
    
    if (!gaddag.loadFromFile(dictPath)) {
        std::cerr << "FAILED: Could not load dictionary from " << dictPath << std::endl;
        return 1;
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Dictionary loaded in " << duration.count() << "ms" << std::endl;

    // Test some known words
    assert(gaddag.contains("JOUER") && "Dictionary should contain 'JOUER'");
    assert(gaddag.contains("MANGER") && "Dictionary should contain 'MANGER'");
    assert(gaddag.contains("XYZWQ") == false && "Dictionary should NOT contain 'XYZWQ'");
    
    // Test case sensitivity (implementation converts to upper)
    assert(gaddag.contains("jouer") && "Dictionary should handle lowercase input (by converting or having mixed case)");

    std::cout << "PASSED: All GADDAG tests passed." << std::endl;
    return 0;
}
