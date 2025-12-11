#include "../engine/engine.h"
#include "../engine/Gaddag.h"
#include "../engine/MoveGenerator.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <sstream>
#include <iomanip>

using namespace Scrabble;

struct BenchmarkCase {
    std::string boardStr;
    std::string rackStr;
};

std::vector<BenchmarkCase> loadBenchmarks(const std::string& path) {
    std::vector<BenchmarkCase> cases;
    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open benchmark file " << path << std::endl;
        return cases;
    }

    std::string line;
    while (std::getline(file, line)) {
        if (line.empty()) continue;
        size_t delimiterPos = line.find('|');
        if (delimiterPos != std::string::npos) {
            std::string board = line.substr(0, delimiterPos);
            std::string rack = line.substr(delimiterPos + 1);
            
            // Trim whitespace
            board.erase(board.find_last_not_of(" \n\r\t") + 1);
            rack.erase(0, rack.find_first_not_of(" \n\r\t"));
            rack.erase(rack.find_last_not_of(" \n\r\t") + 1);
            
            cases.push_back({board, rack});
        }
    }
    return cases;
}

void setupBoard(Board& board, const std::string& boardStr) {
    int idx = 0;
    for (int r = 0; r < 15; ++r) {
        for (int c = 0; c < 15; ++c) {
            if (idx < boardStr.length()) {
                char ch = boardStr[idx++];
                if (ch != '.') {
                    board.setTile(r, c, Tile(ch, 1)); // Dummy value 1
                } else {
                    board.setTile(r, c, Tile()); // Empty
                }
            }
        }
    }
}

int main() {
    std::cout << "=== Scrabble Engine Benchmark ===" << std::endl;

    // 1. Load Dictionary
    std::string dictPath = "assets/dictionnaries/french.txt";
    Gaddag gaddag;
    auto tStart = std::chrono::high_resolution_clock::now();
    if (!gaddag.loadFromFile(dictPath)) {
        std::cerr << "Failed to load dictionary: " << dictPath << std::endl;
        return 1;
    }
    auto tEnd = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(tEnd - tStart).count();
    std::cout << "Dictionary loaded in " << duration << " ms." << std::endl;

    // 2. Load Benchmarks
    std::string benchPath = "assets/benchmarks/synthetic_positions.txt";
    std::vector<BenchmarkCase> cases = loadBenchmarks(benchPath);
    std::cout << "Loaded " << cases.size() << " benchmark positions." << std::endl;

    MoveGenerator generator;
    long long totalDurationUs = 0;
    long long totalMoves = 0;

    std::cout << "\nRunning Benchmarks..." << std::endl;
    std::cout << std::left << std::setw(5) << "#" 
              << std::setw(15) << "Rack" 
              << std::setw(10) << "Moves" 
              << std::setw(10) << "Time(us)" << std::endl;
    std::cout << std::string(40, '-') << std::endl;

    for (size_t i = 0; i < cases.size(); ++i) {
        Board board;
        setupBoard(board, cases[i].boardStr);
        
        std::vector<char> rack(cases[i].rackStr.begin(), cases[i].rackStr.end());
        
        // Warmup? No, we want raw cold/warm performance depending on cache. 
        // Single run per position is fine for macro benchmark.

        tStart = std::chrono::high_resolution_clock::now();
        std::vector<Move> moves = generator.generateMoves(board, rack, gaddag);
        tEnd = std::chrono::high_resolution_clock::now();
        
        long long us = std::chrono::duration_cast<std::chrono::microseconds>(tEnd - tStart).count();
        
        totalDurationUs += us;
        totalMoves += moves.size();

        std::cout << std::left << std::setw(5) << i 
                  << std::setw(15) << cases[i].rackStr 
                  << std::setw(10) << moves.size() 
                  << std::setw(10) << us << std::endl;
    }

    std::cout << std::string(40, '-') << std::endl;
    std::cout << "Total Moves Found: " << totalMoves << std::endl;
    std::cout << "Total Time: " << totalDurationUs << " us" << std::endl;
    double avgTime = cases.empty() ? 0 : (double)totalDurationUs / cases.size();
    std::cout << "Average Time per Position: " << avgTime << " us" << std::endl;

    return 0;
}