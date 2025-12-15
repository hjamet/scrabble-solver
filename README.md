# Scrabble AI Solver (Hybrid Architecture)

A state-of-the-art Scrabble solver designed for maximum performance and future reinforcement learning integration. This project combines a hyper-optimized C++ core with a planned Neural/RL "Brain" and uses Quackle as a ground-truth validator.

## 🚀 Project Overview

This is no longer just a C++ engine. It is a **Hybrid System** built to master Scrabble.
The goal is to build a system that can consistently defeat human players and other engines by leveraging:
- **Core (Speed)**: A C++ engine using GADDAG for instant move generation.
- **Brain (Intelligence)**: A future Neural Network / RL layer for positional evaluation.
- **Oracle (Truth)**: Quackle integration for validation and training data generation.

## 🏗 Architecture

The system is designed with three distinct layers:

### 1. The Core (High-Performance C++)
Located in `src/engine/`.
- **Role**: The muscle. Handles "physics" of the game.
- **Responsibilities**:
    - **Board Representation**: Bit-level optimized board state.
    - **Dictionary**: Memory-efficient GADDAG structure for fast lookups.
    - **Move Generation**: Generating all legal moves in microseconds.
- **Key Metric**: Speed. Must generate 100% of legal moves instantly.

### 2. The Brain (Planned - Python/Torch)
- **Role**: The strategist.
- **Responsibilities**:
    - Evaluating complex positions beyond simple point counting.
    - Managing "Leave" quality (tiles kept for next turn).
    - Opponent modelling.
- **Interface**: Interacts with Core to get candidate moves, checks them, and returns the best strategic choice.

### 3. The Validation (Quackle)
- **Role**: The referee and teacher.
- **Usage**:
    - Used to validate the correctness of our Move Generator.
    - Used to generate "Best Move" data for training the Brain.

## 💡 Technical Decisions

### Dictionary Structure: GADDAG
We selected the **GADDAG** (Directed Acyclic Word Graph with bidirectional generation) data structure over a traditional Trie or DAWG.
- **Why?**: Scrabble move generation requires finding words that "hook" onto existing letters on the board. GADDAG allows generating words *outwards* from any letter (hook), eliminating the need for complex backtracking or "cross-checks" that standard Tries require.
- **Performance**: Provides faster generation for the specific constraints of Scrabble (anchors).

### No "Quackle Wrapper"
We abandoned the idea of simply wrapping Quackle's C++ code.
- **Why?**: We need full control over the memory layout to optimize for our specific RL needs (batch processing, GPU transfer). Building our own lean engine allows this flexibility without technical debt.

## 🛠 Building & Running

### Prerequisites
- Linux / WSL (Ubuntu 20.04+)
- GCC/G++ (C++17 support)
- CMake 3.16+
- Make

### Quick Start
```bash
# Clone
git clone https://github.com/your-username/scrabble-solver.git
cd scrabble-solver

# Build
mkdir build && cd build
cmake ..
make

# Run Test
./simple_test
```

### Benchmarking
To measure the engine's move generation performance:
1. **Generate Synthetic Data**:
    ```bash
    python3 scripts/generate_positions.py
    ```
    This creates `assets/benchmarks/synthetic_positions.txt` with 20 semi-random game positions.

2. **Build & Run Benchmark**:
    ```bash
    make build
    ./build/bench
    ```

## Key Results

| Metric | Our Engine | Quackle (Oracle) | Notes |
| :--- | :--- | :--- | :--- |
| **Dictionary Load** | < 100ms | ~100ms | Binary GADDAG format |
| **Moves Found (Complex)** | 1088 (Rack 2) | 1090 (Rack 2) | 99.8% Accuracy on complex board |
| **Avg Time/Position** | ~2.0 ms | ~1.4 ms | Scaled to 1000 positions |

> [!NOTE]
> Detailed walkthrough of the optimization and verification process is available in `walkthrough.md`. Move generation logic has been significantly improved to support full GADDAG traversal (Left & Right), bringing accuracy close to Quackle for many cases.

## 📂 Project Structure
```
scrabble-solver/
├── assets/
│   └── dictionnaries/   # Lexicons (French ODS, etc.)
├── src/
│   └── engine/          # The C++ Core
│       ├── GADDAG.{h,cpp}       # Dictionary Structure
│       ├── MoveGenerator.{h,cpp} # Move Algorithm
│       └── engine.{h,cpp}        # Board & Core Logic
├── tests/               # Unit & Integration Tests
└── CMakeLists.txt       # Build Configuration
```

## 📜 License
MIT License.
