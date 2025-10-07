cmake_minimum_required(VERSION 3.16)

project(scrabble_solver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Enable testing
enable_testing()

# Add the engine library
add_library(engine src/engine/engine.cpp)

# Find Google Test using CONFIG mode for vcpkg
set(CMAKE_PREFIX_PATH "${CMAKE_CURRENT_SOURCE_DIR}/vcpkg/packages/gtest_x64-windows")
find_package(GTest CONFIG REQUIRED)

# Add the test executable
add_executable(test_main tests/test_main.cpp)
target_link_libraries(test_main engine GTest::gtest GTest::gtest_main)
target_include_directories(test_main PRIVATE src/engine)

# Add test to CTest
add_test(NAME scrabble_tests COMMAND test_main)