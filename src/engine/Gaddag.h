#ifndef GADDAG_H
#define GADDAG_H

#include <vector>
#include <string>
#include <unordered_map>
#include <fstream>
#include <iostream>
#include <algorithm>

namespace Scrabble {

    // Separator character for GADDAG paths
    const char GADDAG_DELIMITER = '+';

    struct Node {
        char letter;
        bool isTerminal; // True if this node marks the end of a valid word (in a GADDAG path sense)
        std::unordered_map<char, Node*> children;

        Node(char c) : letter(c), isTerminal(false) {}
        ~Node();
    };

    class Gaddag {
    private:
        Node* root;

        // Helper to insert a single GADDAG path
        // e.g., for word "CARE", insert "C+ARE", "A C+RE", "R A C+E", "E R A C+"
        void insertPath(const std::string& path);

    public:
        Gaddag();
        ~Gaddag();

        // Load dictionary from a file (one word per line)
        bool loadFromFile(const std::string& filePath);

        // Check if the exact path exists (mostly for debugging/verification)
        Node* getRoot() const { return root; }
        
        // Debug helper: Check if a word exists (by checking one of its GADDAG paths)
        // Note: In a real GADDAG, we generate moves, we don't usually just "check words" directly like a standard Trie,
        // but we can check if "W O R D +" exists.
        bool contains(const std::string& word) const;
    };

}

#endif // GADDAG_H
