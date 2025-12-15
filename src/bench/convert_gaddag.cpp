#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>
#include <cstdint>

#include "alphabetparameters.h"

using namespace Quackle;
using namespace std;

// Minimal reimplementation of GaddagFactory logic without Qt
// Using EnglishAlphabetParameters as the alphabet (A-Z).

const int QUACKLE_MAX_GADDAG_WORDCOUNT = 500000;
const Quackle::Letter internalSeparatorRepresentation = QUACKLE_FIRST_LETTER + QUACKLE_MAXIMUM_ALPHABET_SIZE;

struct Node {
    Quackle::Letter c;
    bool t;
    vector<Node> children;
    int pointer;
    bool lastchild;

    Node() : c(QUACKLE_NULL_MARK), t(false), pointer(0), lastchild(false) {}

    void pushWord(const Quackle::LetterString& word);
    void print(vector<Node*>& nodelist);
};

void Node::pushWord(const Quackle::LetterString& word)
{
    if (word.length() == 0)
    {
        t = true;
        return;
    }

    Quackle::Letter first = Quackle::String::front(word);
    Quackle::LetterString rest = Quackle::String::allButFront(word);
    int index = -1;

    for (size_t i = 0; i < children.size(); i++)
    {
        if (children[i].c == first)
        {
            index = (int)i;
            break;
        }
    }

    if (index == -1)
    {
        Node n;
        n.c = first;
        n.t = false;
        n.pointer = 0;
        n.lastchild = false;
        children.push_back(n);
        index = (int)children.size() - 1;
    }

    children[index].pushWord(rest);
}

void Node::print(vector<Node*>& nodelist)
{
    if (children.size() > 0)
    {
        pointer = (int)nodelist.size();
        children[children.size() - 1].lastchild = true;
    }

    for (size_t i = 0; i < children.size(); i++)
        nodelist.push_back(&children[i]);

    for (size_t i = 0; i < children.size(); i++)
        children[i].print(nodelist);
}

int main(int argc, char** argv) {
    if (argc < 3) {
        cerr << "Usage: " << argv[0] << " <input_dict.txt> <output_dict.gaddag>" << endl;
        return 1;
    }

    string inputPath = argv[1];
    string outputPath = argv[2];

    cout << "Converting " << inputPath << " to " << outputPath << "..." << endl;

    // 1. Setup Alphabet
    // Note: Quackle uses Singletons for DataManager usually, 
    // but here we just need an AlphabetParameters instance to use.
    // However, LetterString::operators might rely on QUACKLE_ALPHABET_PARAMETERS macro 
    // which calls DataManager::self()->alphabetParameters().
    // We MUST initialize DataManager to be safe, or EnglishAlphabetParameters directly.
    // EnglishAlphabetParameters constructor sets up standard A-Z.
    // But we need to inject it into DataManager if global macros use it.
    // Let's rely on creating an instance and hoping global macros aren't mandatory for *simple* operations
    // or set up DataManager.
    // Actually, Quackle::String::left uses iterators, doesn't seem to use global params.
    // BUT Quackle::String::clearBlankness DOES use QUACKLE_ALPHABET_PARAMETERS.
    // We probably don't need clearBlankness here.
    
    // To be safe, let's mock the DataManager or just set the global pointer if possible.
    // Quackle::DataManager singleton... 
    // Taking a shortcut: We will instantiate EnglishAlphabetParameters and use it locally where possible,
    // but Quackle code might be coupled.
    // Fortunately, we are re-implementing logic, so we control it.
    // We only call `m_alphas.encode(word)` which is a member function.

    EnglishAlphabetParameters alphas;
    
    // 2. Read File and Prepare Words
    ifstream infile(inputPath);
    if (!infile.is_open()) {
        cerr << "Failed to open input file." << endl;
        return 1;
    }

    vector<Quackle::LetterString> gaddagizedWords;
    string line;
    int wordCount = 0;

    // Fake Hash (all zeros)
    int32_t hash[4] = {0, 0, 0, 0};

    while (std::getline(infile, line)) {
        // Trim
        line.erase(std::remove_if(line.begin(), line.end(), ::isspace), line.end());
        if (line.empty()) continue;
        
        // Uppercase
        std::transform(line.begin(), line.end(), line.begin(), ::toupper);

        // Encode
        // Convert std::string to UVString (std::string)
        UVString uvWord = line;
        UVString leftover;
        Quackle::LetterString encoded = alphas.encode(uvWord, &leftover);
        
        if (!leftover.empty()) {
            cerr << "Warning: Skipping unencodable word: " << line << endl;
            continue;
        }

        // GADDAG-ize
        // Logic from GaddagFactory::pushWord
        for (unsigned i = 1; i <= encoded.length(); i++)
        {
            Quackle::LetterString newword;

            for (int j = i - 1; j >= 0; j--)
                newword.push_back(encoded[j]);

            if (i < encoded.length())
            {
                newword.push_back(internalSeparatorRepresentation);
                for (unsigned j = i; j < encoded.length(); j++)
                    newword.push_back(encoded[j]);
            }
            gaddagizedWords.push_back(newword);
        }
        wordCount++;
    }
    infile.close();
    cout << "Read " << wordCount << " words." << endl;

    // 3. Sort
    cout << "Sorting..." << endl;
    std::sort(gaddagizedWords.begin(), gaddagizedWords.end());

    // 4. Generate Tree
    cout << "Generating Tree..." << endl;
    Node root;
    // Root setup from GaddagFactory ctor
    root.t = false;
    root.c = QUACKLE_NULL_MARK;
    root.pointer = 0;
    root.lastchild = true;

    for (const auto& w : gaddagizedWords) {
        root.pushWord(w);
    }

    // 5. Write Index
    cout << "Writing Index..." << endl;
    vector<Node*> nodelist;
    nodelist.push_back(&root);
    root.print(nodelist);

    ofstream out(outputPath, ios::out | ios::binary);
    if (!out.is_open()) {
        cerr << "Failed to open output file." << endl;
        return 1;
    }

    out.put(1); // Version 1
    // Write Hash (16 bytes)
    out.write(reinterpret_cast<char*>(hash), 16);

    for (unsigned int i = 0; i < nodelist.size(); i++)
    {
        unsigned int p = (unsigned int)(nodelist[i]->pointer);
        if (p != 0)
            p -= i; // offset indexing

        char bytes[4];
        unsigned char n1 = (p & 0x00FF0000) >> 16;
        unsigned char n2 = (p & 0x0000FF00) >> 8;
        unsigned char n3 = (p & 0x000000FF) >> 0;
        unsigned char n4; 

        n4 = nodelist[i]->c;
        if (n4 == internalSeparatorRepresentation)
            n4 = QUACKLE_NULL_MARK;

        if (nodelist[i]->t)
            n4 |= 64;

        if (nodelist[i]->lastchild)
            n4 |= 128;

        bytes[0] = n1; bytes[1] = n2; bytes[2] = n3; bytes[3] = n4;
        out.write(bytes, 4);
    }
    out.close();

    cout << "Done. Wrote " << nodelist.size() << " nodes." << endl;
    return 0;
}
