cmake_minimum_required(VERSION 3.16)

project(scrabble_solver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include Quackle
add_subdirectory(quackle)

# Add the engine library
add_library(engine 
    src/engine/engine.cpp
    src/engine/Gaddag.cpp
    src/engine/MoveGenerator.cpp
)

# Create a simple test executable without Google Test for now
add_executable(simple_test tests/simple_test.cpp)
target_link_libraries(simple_test engine)
target_include_directories(simple_test PRIVATE src/engine)

# Add GADDAG test
add_executable(test_gaddag tests/test_gaddag.cpp)
target_link_libraries(test_gaddag engine)
target_include_directories(test_gaddag PRIVATE src/engine)

# Add MoveGenerator test
add_executable(test_move_generator tests/test_move_generator.cpp)
target_link_libraries(test_move_generator engine)
target_include_directories(test_move_generator PRIVATE src/engine)

# Add Benchmark tool
add_executable(bench src/bench/bench.cpp)
target_link_libraries(bench engine)

# Tool to convert dictionary for Quackle
add_executable(convert_gaddag src/bench/convert_gaddag.cpp)
target_link_libraries(convert_gaddag libquackle)
target_include_directories(convert_gaddag PRIVATE quackle)

# Quackle Benchmark
add_executable(quackle_bench src/bench/quackle_bench.cpp)
target_link_libraries(quackle_bench libquackle)
target_include_directories(quackle_bench PRIVATE quackle)

target_include_directories(bench PRIVATE src/engine)