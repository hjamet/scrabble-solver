# Makefile for Scrabble Solver
# Provides targets for building, testing, and managing the project

# Variables
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -O2
BUILD_DIR = build
SRC_DIR = src
TEST_DIR = tests
ENGINE_LIB = $(BUILD_DIR)/libengine.a
TEST_EXEC = $(BUILD_DIR)/simple_test
GTEST_EXEC = $(BUILD_DIR)/test_main

# Default target
.PHONY: all
all: check-deps build test

# Check if required tools are installed
.PHONY: check-deps
check-deps:
	@echo "Checking dependencies..."
	@command -v g++ >/dev/null 2>&1 || { echo "Error: g++ is required but not installed. Run 'make install-deps'"; exit 1; }
	@command -v make >/dev/null 2>&1 || { echo "Error: make is required but not installed. Run 'make install-deps'"; exit 1; }
	@echo "✓ g++ compiler found"
	@echo "✓ make found"
	@if [ ! -d "$(BUILD_DIR)" ]; then mkdir -p $(BUILD_DIR); fi
	@echo "✓ Build directory ready"

# Install system dependencies
.PHONY: install-deps
install-deps:
	@echo "Installing system dependencies..."
	sudo apt update
	sudo apt install -y build-essential libgtest-dev cmake
	@echo "✓ Dependencies installed"

# Check if CMake is available, download if needed
.PHONY: check-cmake
check-cmake:
	@if ! command -v cmake >/dev/null 2>&1; then \
		echo "CMake not found. Downloading..."; \
		if [ ! -d "cmake-3.27.8-linux-x86_64" ]; then \
			wget -qO- https://github.com/Kitware/CMake/releases/download/v3.27.8/cmake-3.27.8-linux-x86_64.tar.gz | tar -xz; \
		fi; \
		export PATH=$$PWD/cmake-3.27.8-linux-x86_64/bin:$$PATH; \
		echo "✓ CMake downloaded and ready"; \
	else \
		echo "✓ CMake found"; \
	fi

# Build the project using CMake
.PHONY: build
build: check-deps check-cmake
	@echo "Building project..."
	@if command -v cmake >/dev/null 2>&1; then \
		cmake -B $(BUILD_DIR); \
		cmake --build $(BUILD_DIR); \
	else \
		export PATH=$$PWD/cmake-3.27.8-linux-x86_64/bin:$$PATH; \
		cmake -B $(BUILD_DIR); \
		cmake --build $(BUILD_DIR); \
	fi
	@echo "✓ Build completed"

# Build with Google Test (if available)
.PHONY: build-gtest
build-gtest: check-deps check-cmake
	@echo "Building with Google Test..."
	@if pkg-config --exists gtest; then \
		echo "✓ Google Test found, building with GTest"; \
		cp CMakeLists.txt CMakeLists.txt.backup; \
		sed 's/simple_test/test_main/g; s/# Find Google Test using standard system packages/find_package(GTest REQUIRED)/g; s/add_executable(simple_test/# Add the test executable\nadd_executable(test_main/g; s/target_link_libraries(simple_test/target_link_libraries(test_main engine GTest::gtest GTest::gtest_main)/g; s/target_include_directories(simple_test/target_include_directories(test_main/g' CMakeLists.txt > CMakeLists.gtest; \
		mv CMakeLists.gtest CMakeLists.txt; \
		if command -v cmake >/dev/null 2>&1; then \
			cmake -B $(BUILD_DIR); \
			cmake --build $(BUILD_DIR); \
		else \
			export PATH=$$PWD/cmake-3.27.8-linux-x86_64/bin:$$PATH; \
			cmake -B $(BUILD_DIR); \
			cmake --build $(BUILD_DIR); \
		fi; \
		mv CMakeLists.txt.backup CMakeLists.txt; \
		echo "✓ Build with Google Test completed"; \
	else \
		echo "⚠ Google Test not found, building simple version"; \
		$(MAKE) build; \
	fi

# Run simple tests
.PHONY: test
test: build
	@echo "Running tests..."
	@if [ -f "$(TEST_EXEC)" ]; then \
		./$(TEST_EXEC); \
		echo "✓ All tests passed"; \
	else \
		echo "Error: Test executable not found. Run 'make build' first."; \
		exit 1; \
	fi

# Run Google Test (if available)
.PHONY: test-gtest
test-gtest: build-gtest
	@echo "Running Google Test..."
	@if [ -f "$(GTEST_EXEC)" ]; then \
		./$(GTEST_EXEC); \
		echo "✓ All Google Tests passed"; \
	else \
		echo "⚠ Google Test executable not found, running simple tests"; \
		$(MAKE) test; \
	fi

# Run all tests (both simple and Google Test if available)
.PHONY: test-all
test-all: test
	@if pkg-config --exists gtest; then \
		echo ""; \
		echo "Running Google Test as well..."; \
		$(MAKE) test-gtest; \
	fi

# Clean build artifacts
.PHONY: clean
clean:
	@echo "Cleaning build artifacts..."
	@rm -rf $(BUILD_DIR)
	@rm -f *.o
	@rm -f simple_test
	@echo "✓ Clean completed"

# Deep clean (including downloaded CMake)
.PHONY: distclean
distclean: clean
	@echo "Deep cleaning..."
	@rm -rf cmake-3.27.8-linux-x86_64
	@echo "✓ Deep clean completed"

# Show help
.PHONY: help
help:
	@echo "Scrabble Solver - Available targets:"
	@echo ""
	@echo "  all          - Check dependencies, build, and test (default)"
	@echo "  check-deps   - Check if required tools are installed"
	@echo "  install-deps - Install system dependencies (requires sudo)"
	@echo "  build        - Build the project using CMake"
	@echo "  build-gtest  - Build with Google Test (if available)"
	@echo "  test         - Run simple tests"
	@echo "  test-gtest   - Run Google Test (if available)"
	@echo "  test-all     - Run all available tests"
	@echo "  clean        - Remove build artifacts"
	@echo "  distclean    - Remove all generated files including CMake"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Examples:"
	@echo "  make              # Build and test everything"
	@echo "  make install-deps # Install dependencies first"
	@echo "  make test         # Just run tests"
	@echo "  make clean        # Clean build files"

# Show project status
.PHONY: status
status:
	@echo "Scrabble Solver - Project Status"
	@echo "================================"
	@echo "Build directory: $(BUILD_DIR)"
	@echo "Source directory: $(SRC_DIR)"
	@echo "Test directory: $(TEST_DIR)"
	@echo ""
	@echo "Dependencies:"
	@command -v g++ >/dev/null 2>&1 && echo "✓ g++ compiler" || echo "✗ g++ compiler"
	@command -v make >/dev/null 2>&1 && echo "✓ make" || echo "✗ make"
	@command -v cmake >/dev/null 2>&1 && echo "✓ cmake" || echo "✗ cmake (will download if needed)"
	@pkg-config --exists gtest >/dev/null 2>&1 && echo "✓ Google Test" || echo "✗ Google Test"
	@echo ""
	@echo "Build artifacts:"
	@[ -f "$(ENGINE_LIB)" ] && echo "✓ Engine library" || echo "✗ Engine library"
	@[ -f "$(TEST_EXEC)" ] && echo "✓ Simple test executable" || echo "✗ Simple test executable"
	@[ -f "$(GTEST_EXEC)" ] && echo "✓ Google Test executable" || echo "✗ Google Test executable"
