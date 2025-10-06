# Scrabble AI Solver

An ultra-high-performance Scrabble solver designed to always win. This project combines a high-performance C engine with Monte Carlo Tree Search (MCTS) algorithms and a modern web interface for testing and gameplay.

## Project Overview

This is a side project focused on creating the most powerful Scrabble solver possible. The goal is to build a system that can consistently defeat human players by leveraging:

- **High-performance C engine** for position evaluation and move generation
- **Monte Carlo Tree Search (MCTS)** for strategic decision making
- **Modern web interface** for testing, visualization, and online gameplay
- **Multi-language support** for international Scrabble variants

## Architecture

The project is structured as a multi-component system:

```
scrabble-solver/
├── src/engine/      # C-based core engine (position evaluation, move generation)
├── mcts/            # C-based Monte Carlo Tree Search implementation
├── web-interface/   # Node.js web application for testing and gameplay
├── dictionaries/    # Word lists and dictionaries for multiple languages
├── tests/           # Comprehensive test suite
└── docs/            # Documentation and analysis
```


## Principes de Conception Stratégique

### Noyau et API
Le moteur (`src/engine/`) est développé comme une bibliothèque C autonome. Toute interaction avec le moteur doit passer par une API publique unique (`engine.h`), garantissant une forte encapsulation. Cette approche permet :
- Une séparation claire entre l'interface publique et l'implémentation interne
- Une évolution indépendante des composants
- Une facilité de test et de maintenance
- Une réutilisabilité maximale du code

### Représentation du Plateau
L'approche adoptée utilise une représentation à deux niveaux pour optimiser les performances :
- **Grille statique 15x15** : Contient les informations sur les bonus (lettre/score double/triple, mot double/triple). Cette grille est en lecture seule après l'initialisation.
- **Grille dynamique 15x15** : Contient les tuiles posées sur le plateau. Cette grille est modifiée dynamiquement pendant le jeu.

Cette séparation optimise les accès mémoire en évitant de mélanger des données statiques et dynamiques, améliorant ainsi les performances du cache processeur.

### Manipulation d'État Do/Undo
Le projet utilise un mécanisme `do/undo` pour la manipulation de l'état du jeu. Cette approche :
- Évite les copies coûteuses du plateau complet
- Est fondamentale pour la performance de l'algorithme MCTS qui explore de nombreux états
- Permet un retour rapide à l'état précédent après évaluation d'un coup
- Optimise l'utilisation mémoire en ne stockant que les différences entre états

### Core Components

- **`engine/`**: High-performance C library for:
  - Board state representation and manipulation
  - Move generation and validation
  - Score calculation with bonus tiles
  - Position evaluation and ranking
  - Dictionary lookup optimization

- **`mcts/`**: Monte Carlo Tree Search implementation in C for:
  - Strategic move selection
  - Long-term planning
  - Opponent modeling
  - Endgame optimization

- **`web-interface/`**: Node.js application inspired by [scrabble-solver](https://github.com/kamilmielnik/scrabble-solver) for:
  - Interactive board visualization
  - Move testing and validation
  - Performance monitoring
  - Online multiplayer support
  - Real-time analysis display

## Development Roadmap

### Phase 1: Foundation (Current)
- [ ] Project structure setup
- [ ] Basic C engine architecture
- [ ] Core data structures (board, tiles, moves)
- [ ] Dictionary loading and indexing

### Phase 2: Core Engine
- [ ] Move generation algorithms
- [ ] Score calculation system
- [ ] Position evaluation functions
- [ ] Performance optimization

### Phase 3: Web Interface
- [ ] Basic web interface for testing
- [ ] Board visualization
- [ ] Move input and validation
- [ ] Engine integration

### Phase 4: MCTS Implementation
- [ ] Monte Carlo Tree Search algorithm
- [ ] Strategic decision making
- [ ] Opponent modeling
- [ ] Endgame optimization

### Phase 5: Advanced Features
- [ ] Multi-language support
- [ ] Online multiplayer
- [ ] Performance analytics
- [ ] AI difficulty levels

## Technical Specifications

### Performance Goals
- **Move generation**: < 1ms for typical positions
- **Position evaluation**: < 10ms for complex positions
- **MCTS search**: 1000+ simulations per second
- **Memory usage**: < 100MB for full game state

### Supported Languages
- English (TWL06, SOWPODS)
- French (ODS8)
- German
- Spanish
- Additional languages as needed

### Game Variants
- Standard Scrabble
- Super Scrabble
- Scrabble variants with different board sizes
- Custom rule sets

## Getting Started

### Prerequisites
- C compiler (GCC 9+ or Clang 10+)
- CMake 3.16+
- Git

### Environment Setup (Windows)

For Windows development, we use MSYS2 to provide a complete C development environment.

#### Quick Installation

Run the automated installation script as administrator:

```powershell
# Run as administrator
.\install-dev-env.ps1
```

This script will:
1. Download and install MSYS2 automatically
2. Create an installation script for development tools
3. Add MSYS2 to your system PATH

#### Manual Installation

If you prefer manual installation:

1. **Install MSYS2**: Download from [msys2.org](https://www.msys2.org/) and run the installer
2. **Launch MSYS2 UCRT64** from the Start Menu
3. **Install development tools**:
   ```bash
   # Update package manager
   pacman -Syu
   pacman -Su
   
   # Install C development tools
   pacman -S --needed base-devel mingw-w64-ucrt-x86_64-toolchain
   
   # Install CMake and additional tools
   pacman -S --needed mingw-w64-ucrt-x86_64-cmake mingw-w64-ucrt-x86_64-gdb mingw-w64-ucrt-x86_64-git
   ```

#### Verify Installation

Test your C environment:

```bash
# Test compilation
gcc --version
make --version
cmake --version
gdb --version
```

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/scrabble-solver.git
cd scrabble-solver

# Build the C engine
mkdir build && cd build
cmake ..
make -j$(nproc)

# Run tests
./test_main
```

### Project Structure

The project follows a clean, modular architecture:

```
scrabble-solver/
├── src/engine/           # C-based core engine
│   ├── engine.h         # Public API interface
│   └── engine.c         # Engine implementation
├── tests/               # Test suite
│   └── test_main.c      # Main test executable
├── build/               # Build artifacts (generated)
├── CMakeLists.txt       # CMake build configuration
├── install-dev-env.ps1  # Windows development setup
└── README.md           # This file
```

### Important Files

- **`src/engine/engine.h`** : Public API interface for the Scrabble engine
  - *Role* : Defines all public functions and data structures
  - *Usage* : Include this header to use the engine in your code
  - *Example* : `#include "engine.h"` — *provides access to all engine functionality*

- **`src/engine/engine.c`** : Core engine implementation
  - *Role* : Contains the actual implementation of all engine functions
  - *Central nodes* : Board representation, move generation, score calculation
  - *Example* : `make` — *compiles the engine into a library*

- **`CMakeLists.txt`** : Build system configuration
  - *Role* : Defines how to compile the project and its dependencies
  - *Points of attention* : Library linking, compiler flags, test configuration
  - *Example* : `cmake ..` — *generates build files for your platform*

- **`tests/test_main.c`** : Test executable entry point
  - *Role* : Main function for running all tests
  - *Usage* : Compile and run to verify engine functionality
  - *Example* : `./test_main` — *executes the complete test suite*

### Main Commands

- Build the project:

```bash
mkdir build && cd build
cmake ..
make
```

*Compiles the engine library and test executable using CMake.*

- Run tests:

```bash
cd build
./test_main
```

*Executes the test suite to verify engine functionality.*

- Clean build:

```bash
rm -rf build
```

*Removes all build artifacts for a fresh compilation.*

### Development Workflow

1. **Modify engine code** in `src/engine/`
2. **Update tests** in `tests/` as needed
3. **Build and test** using the commands above
4. **Verify functionality** before committing changes

## Development Guidelines

### Code Standards
- **Language**: All code written in English
- **C Code**: Follow GNU coding standards
- **JavaScript**: Use ESLint and Prettier
- **Documentation**: Comprehensive inline documentation

### Testing
- Unit tests for all core functions
- Integration tests for engine components
- Performance benchmarks
- End-to-end testing for web interface

### Performance Optimization
- Profile-guided optimization for C code
- SIMD instructions where applicable
- Memory pool allocation
- Cache-friendly data structures

## Contributing

This project is managed by Nicolas and the repository owner. Contributions are welcome for:

- Performance optimizations
- Additional language support
- Bug fixes and improvements
- Documentation enhancements

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

## Inspiration

The web interface draws inspiration from [kamilmielnik/scrabble-solver](https://github.com/kamilmielnik/scrabble-solver), which provides an excellent foundation for Scrabble visualization and interaction. However, our implementation uses a custom high-performance C engine rather than JavaScript-based solving.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [kamilmielnik/scrabble-solver](https://github.com/kamilmielnik/scrabble-solver) for interface inspiration
- Scrabble community for dictionary resources
- Open source contributors and maintainers

---

*This is a passion project focused on pushing the boundaries of Scrabble AI performance. The goal is not just to win, but to understand and master the game at the highest level.*
