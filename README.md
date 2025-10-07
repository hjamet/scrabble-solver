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

- **`engine/`**: High-performance C++ library for:
  - Board state representation and manipulation
  - Move generation and validation
  - Score calculation with bonus tiles
  - Position evaluation and ranking
  - Dictionary lookup optimization

### Data Structures

The engine implements a clean separation of concerns with the following core structures:

- **`Bonus` enum class**: Represents special board positions (None, DoubleLetter, TripleLetter, DoubleWord, TripleWord)
- **`Tile` struct**: Represents a game tile with letter and point value, including support for empty tiles and blanks
- **`Move` struct**: Encapsulates a complete move with position, orientation, and tiles to place
- **`Board` class**: Implements the two-level board representation:
  - Static bonus board (read-only after initialization)
  - Dynamic tile board (modified during gameplay)
  - Provides methods for tile placement, retrieval, and position validation

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
- [x] Project structure setup
- [x] Basic C++ engine architecture
- [x] Core data structures (board, tiles, moves)
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
- Ubuntu 20.04+ or WSL with Ubuntu
- GCC/G++ compiler (build-essential package)
- CMake 3.16+ (automatically downloaded if not available)
- Git
- Make (usually included with build-essential)

### Environment Setup (Linux/WSL)

This project is designed to run on Linux systems, including WSL (Windows Subsystem for Linux) with Ubuntu.

#### Installation Steps

1. **Update system packages**:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Install build tools and dependencies**:
   ```bash
   sudo apt install -y build-essential
   ```

3. **Verify installation**:
   ```bash
   g++ --version
   make --version
   ```

Both commands should display version information without errors. CMake will be automatically downloaded by the build script if needed.

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/scrabble-solver.git
cd scrabble-solver

# Install dependencies (requires sudo)
make install-deps

# Build and test the project
make

# Or step by step:
# make check-deps    # Check if tools are installed
# make build         # Build the project
# make test          # Run tests
```

### Project Structure

The project follows a clean, modular architecture:

```
scrabble-solver/
├── src/engine/           # C++-based core engine
│   ├── engine.h         # Public API interface
│   └── engine.cpp       # Engine implementation
├── tests/               # Test suite
│   ├── test_main.cpp    # Google Test executable
│   └── simple_test.cpp  # Simple test executable
├── build/               # Build artifacts (generated)
├── Makefile             # Build automation
├── CMakeLists.txt       # CMake build configuration
└── README.md           # This file
```

### Important Files

- **`src/engine/engine.h`** : Public API interface for the Scrabble engine
  - *Role* : Defines all public functions and data structures
  - *Usage* : Include this header to use the engine in your code
  - *Example* : `#include "engine.h"` — *provides access to all engine functionality*

- **`src/engine/engine.cpp`** : Core engine implementation
  - *Role* : Contains the actual implementation of all engine functions
  - *Central nodes* : Board representation, move generation, score calculation
  - *Example* : `cmake --build .` — *compiles the engine into a library*

- **`CMakeLists.txt`** : Build system configuration
  - *Role* : Defines how to compile the project and its dependencies
  - *Points of attention* : Library linking, compiler flags, test configuration
  - *Example* : `cmake -B build` — *generates build files for GCC on Linux*

- **`tests/simple_test.cpp`** : Simple test executable entry point
  - *Role* : Main function for running all tests without external dependencies
  - *Usage* : Compile and run to verify engine functionality
  - *Example* : `./build/simple_test` — *executes the complete test suite*

- **`Makefile`** : Build automation system
  - *Role* : Provides targets for building, testing, and managing the project
  - *Usage* : Use make commands to build, test, and clean the project
  - *Example* : `make` — *builds the project and runs all tests*
  - *Available targets* : `make help` — *shows all available commands*

### Main Commands

- Build and test the project (recommended method):

```bash
make
```

*Automatically checks dependencies, builds the project, and runs all tests.*

- Install system dependencies:

```bash
make install-deps
```

*Installs build-essential, Google Test, and CMake (requires sudo).*

- Check project status:

```bash
make status
```

*Shows the status of dependencies and build artifacts.*

- Build only:

```bash
make build
```

*Builds the project without running tests.*

- Run tests only:

```bash
make test
```

*Runs the simple test suite.*

- Run Google Test (if available):

```bash
make test-gtest
```

*Runs the Google Test suite.*

- Clean build artifacts:

```bash
make clean
```

*Removes build directory and temporary files.*

- Show all available commands:

```bash
make help
```

*Displays all available make targets with descriptions.*

## Services & Databases

This project is currently a standalone C++ library with no external services or databases. All game state is managed in memory.

## Environment Variables

No environment variables are required for basic operation. The project uses standard C++ compilation with no external configuration needed.

## Guide de déploiement / exécution

### Local Development

1. **Clone and setup**:
   ```bash
   git clone https://github.com/your-username/scrabble-solver.git
   cd scrabble-solver
   make install-deps  # Install dependencies (requires sudo)
   ```

2. **Build and test**:
   ```bash
   make  # Builds and runs all tests
   ```

3. **Development workflow**:
   ```bash
   make status    # Check project status
   make build     # Build only
   make test      # Run tests only
   make clean     # Clean build artifacts
   ```

### Development Workflow

1. **Modify engine code** in `src/engine/`
2. **Update tests** in `tests/` as needed
3. **Build and test** using `make`
4. **Verify functionality** before committing changes

## Changelog sommaire

### Version 1.2.0 - Makefile et Google Test
- **Ajout** d'un Makefile complet pour l'automatisation du build
- **Support** de Google Test avec installation automatique
- **Cibles** multiples : build, test, clean, status, help
- **Vérification** automatique des dépendances
- **Suppression** du script bash au profit du Makefile
- **Amélioration** de l'expérience développeur

### Version 1.1.0 - Migration vers Linux/WSL
- **Migration complète** de Windows/MSVC vers Linux/GCC
- **Suppression** des scripts PowerShell (`build.ps1`, `install-gtest.ps1`)
- **Suppression** des dépendances vcpkg
- **Création** d'un système de test simple sans dépendances externes
- **Mise à jour** complète de la documentation pour Linux/WSL
- **Support** de CMake avec téléchargement automatique si nécessaire

### Version 1.0.0 - Version initiale
- Implémentation du moteur de base en C++
- Structure de données pour le plateau de Scrabble
- Tests unitaires avec Google Test
- Configuration de build Windows/MSVC

## Development Guidelines

### Code Standards
- **Language**: All code written in English
- **C Code**: Follow GNU coding standards
- **JavaScript**: Use ESLint and Prettier
- **Documentation**: Comprehensive inline documentation

### Testing
- **Google Test framework** for robust unit testing
- **Isolated test execution** - each test runs independently
- **Detailed failure reporting** with clear error messages
- **CTest integration** for automated test running
- **XML test reports** for CI/CD integration
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
