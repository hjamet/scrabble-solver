#include "Gaddag.h"
#include <cstdint>

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


    // --- Binary Serialization Helpers ---

    void saveNode(Node* node, std::ofstream& out) {
        // Format: [char letter] [bool isTerminal] [uint8_t numChildren] [Children...]
        out.write(&node->letter, sizeof(char));
        out.write(reinterpret_cast<char*>(&node->isTerminal), sizeof(bool));
        
        uint8_t numChildren = (uint8_t)node->children.size();
        out.write(reinterpret_cast<char*>(&numChildren), sizeof(uint8_t));

        for (auto& pair : node->children) {
            // Write Child Key (Char)
            out.write(&pair.first, sizeof(char));
            // Recursively write child node
            saveNode(pair.second, out);
        }
    }

    Node* loadNode(std::ifstream& in) {
        char letter;
        bool isTerminal;
        uint8_t numChildren;

        in.read(&letter, sizeof(char));
        in.read(reinterpret_cast<char*>(&isTerminal), sizeof(bool));
        in.read(reinterpret_cast<char*>(&numChildren), sizeof(uint8_t));

        if (in.fail()) return nullptr;

        Node* node = new Node(letter);
        node->isTerminal = isTerminal;

        for (int i = 0; i < numChildren; ++i) {
            char key;
            in.read(&key, sizeof(char));
            Node* child = loadNode(in);
            if (child) {
                node->children[key] = child;
            }
        }
        return node;
    }

    bool Gaddag::saveBinary(const std::string& filePath) {
        std::ofstream file(filePath, std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "Error opening file for writing: " << filePath << std::endl;
            return false;
        }
        
        if (root) {
            saveNode(root, file);
        }
        
        file.close();
        std::cout << "GADDAG Saved to binary: " << filePath << std::endl;
        return true;
    }

    bool Gaddag::loadBinary(const std::string& filePath) {
        std::ifstream file(filePath, std::ios::binary);
        if (!file.is_open()) {
            std::cerr << "Error opening file for reading: " << filePath << std::endl;
            return false;
        }

        // Clean up existing
        delete root;
        
        root = loadNode(file);
        
        file.close();
        if (root) {
            std::cout << "GADDAG Loaded from binary." << std::endl;
            return true;
        }
        return false;
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
