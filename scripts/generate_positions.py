import random
import os
import sys

# Configuration
DICT_PATH = 'assets/dictionnaries/french.txt'
OUTPUT_PATH = 'assets/benchmarks/synthetic_positions.txt'
NUM_POSITIONS = 20
MOVES_PER_GAME = 15  # Simulate a mid-game state

class Board:
    def __init__(self):
        self.size = 15
        self.grid = [['.' for _ in range(self.size)] for _ in range(self.size)]
        self.words = set()

    def is_empty(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == '.'

    def get(self, r, c):
        if 0 <= r < self.size and 0 <= c < self.size:
            return self.grid[r][c]
        return None

    def place(self, word, row, col, horizontal):
        # Tentative placement check
        new_grid = [row[:] for row in self.grid]
        
        # Check main word placement
        for i, char in enumerate(word):
            r = row if horizontal else row + i
            c = col + i if horizontal else col
            
            if not (0 <= r < 15 and 0 <= c < 15):
                return False
            
            existing = new_grid[r][c]
            if existing != '.' and existing != char:
                return False
            
            new_grid[r][c] = char

        # Basic connectivity check (simplistic)
        # 1. Must touch at least one existing tile (unless board empty)
        # 2. Must not create invalid adjacent words (We will SKIP this for speed/simplicity in this fuzzer version, relying on the fact we build VALID words mostly)
        # Ideally, we should check perpendicular words.
        
        # ... For this sprint, we assume if it fits and connects, it's "good enough" for benchmarking search speed.
        # But wait, if we create garbage boards, the benchmark is less useful.
        # Let's add a quick "connected" check.
        
        connected = False
        is_first_move = all(c == '.' for r in self.grid for c in r)
        
        if is_first_move:
             # Must pass through center 7,7
             center_covered = False
             for i in range(len(word)):
                r = row if horizontal else row + i
                c = col + i if horizontal else col
                if r == 7 and c == 7:
                    center_covered = True
             if not center_covered: return False
             connected = True
        else:
            # Must touch existing
            for i, char in enumerate(word):
                r = row if horizontal else row + i
                c = col + i if horizontal else col
                if self.grid[r][c] != '.':
                    connected = True
                else:
                    # Check neighbors
                    nbqs = [(r+1,c), (r-1,c), (r,c+1), (r,c+1)]
                    for nr, nc in nbqs:
                        if 0 <= nr < 15 and 0 <= nc < 15 and self.grid[nr][nc] != '.':
                            connected = True
        
        if not connected: return False

        # Apply
        self.grid = new_grid
        return True

    def to_string(self):
        return "".join("".join(row) for row in self.grid)

def load_dictionary(path):
    print(f"Loading dictionary from {path}...")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            words = [line.strip().upper() for line in f if 2 <= len(line.strip()) <= 15]
        return words
    except FileNotFoundError:
        print("Dictionary not found!")
        sys.exit(1)

def generate_rack():
    # Distribution standard simplifiée (French Scrabble-ish)
    bag = "EEEEEEEEEEEEEEAAAAAAAAAIIIIIIIINNNNNNOOOOOORRRRRRSSSSSSTTTTTTUUUUUULLLLDDDMMPPBBCCFFGGHHJKQVWXYZ??"
    return "".join(random.sample(bag, 7))

def generate_game(dictionary):
    board = Board()
    
    # Place random words
    attempts = 0
    words_placed = 0
    
    while words_placed < MOVES_PER_GAME and attempts < 1000:
        attempts += 1
        word = random.choice(dictionary)
        
        # Random pos
        row = random.randint(0, 14)
        col = random.randint(0, 14)
        horizontal = random.choice([True, False])
        
        if board.place(word, row, col, horizontal):
            words_placed += 1
            # print(f"Placed {word} at {row},{col}")
            
    return board

def main():
    if not os.path.exists(os.path.dirname(OUTPUT_PATH)):
        os.makedirs(os.path.dirname(OUTPUT_PATH))

    dictionary = load_dictionary(DICT_PATH)
    
    print(f"Generating {NUM_POSITIONS} positions...")
    
    with open(OUTPUT_PATH, 'w') as f:
        for i in range(NUM_POSITIONS):
            board = generate_game(dictionary)
            rack = generate_rack()
            
            # Format: BOARD_STRING | RACK
            line = f"{board.to_string()} | {rack}\n"
            f.write(line)
            
            if (i+1) % 5 == 0:
                print(f"Generated {i+1} positions.")

    print(f"Done! Saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
