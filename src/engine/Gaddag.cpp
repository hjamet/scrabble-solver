#include "Gaddag.h"

namespace Scrabble {

    Node::~Node() {
        for (auto& pair : children) {
            delete pair.second;
        }
    }

    Gaddag::Gaddag() {
        root = new Node(0); // Root node
    }

    Gaddag::~Gaddag() {
        delete root;
    }

    void Gaddag::insertPath(const std::string& path) {
        Node* current = root;
        for (char c : path) {
            if (current->children.find(c) == current->children.end()) {
                current->children[c] = new Node(c);
            }
            current = current->children[c];
        }
        current->isTerminal = true;
    }

    bool Gaddag::loadFromFile(const std::string& filePath) {
        std::ifstream file(filePath);
        if (!file.is_open()) {
            std::cerr << "Error: Could not open dictionary file: " << filePath << std::endl;
            return false;
        }

        std::string word;
        while (std::getline(file, word)) {
            // Remove any carriage returns or whitespace
            word.erase(std::remove_if(word.begin(), word.end(), ::isspace), word.end());
            
            if (word.empty()) continue;

            // Convert to uppercase if needed (assuming standard is uppercase)
            std::transform(word.begin(), word.end(), word.begin(), ::toupper);

            // Generate GADDAG paths
            // Gordon's Algorithm:
            // For word w_1...w_n, add paths:
            // REV(w_1...w_j) + w_{j+1}...w_n  for j in 1..n
            
            // Example "CARE":
            // j=0 ('C'): C + A R E
            // j=1 ('A'): A C + R E
            // j=2 ('R'): R A C + E
            // j=3 ('E'): E R A C +
            
            // NOTE: The delimiter is strictly between the prefix (reversed) and the suffix.
            // If we are at the first letter (j=0), prefix is just that letter.
            
            // Actually, let's look at the standard formal definition:
            // Path: Rev(Prefix) + Suffix
            // For "CARE":
            // Prefix "C", Suffix "ARE" -> "C+ARE"
            // Prefix "CA", Suffix "RE" -> "AC+RE"
            // Prefix "CAR", Suffix "E" -> "RAC+E"
            // Prefix "CARE", Suffix "" -> "ERAC+"
            
            for (size_t j = 1; j <= word.length(); ++j) {
                std::string prefix = word.substr(0, j);
                std::string suffix = (j < word.length()) ? word.substr(j) : "";
                
                std::string path = prefix;
                std::reverse(path.begin(), path.end());
                path += GADDAG_DELIMITER;
                path += suffix;
                
                insertPath(path);
            }
        }
        
        file.close();
        std::cout << "GADDAG Loaded successfully." << std::endl;
        return true;
    }

    bool Gaddag::contains(const std::string& word) const {
        // Normalize to uppercase
        std::string upperWord = word;
        std::transform(upperWord.begin(), upperWord.end(), upperWord.begin(), ::toupper);

        // To check if a word exists, we can just check one canonical path.
        // e.g., the full reverse path: REVERSE(WORD) + ""
        std::string checkPath = upperWord;
        std::reverse(checkPath.begin(), checkPath.end());
        checkPath += GADDAG_DELIMITER;
        
        Node* current = root;
        for (char c : checkPath) {
            if (current->children.find(c) == current->children.end()) {
                return false;
            }
            current = current->children[c];
        }
        return current->isTerminal;
    }

}
