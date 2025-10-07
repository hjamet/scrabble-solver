cmake_minimum_required(VERSION 3.16)

project(scrabble_solver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the engine library
add_library(engine src/engine/engine.cpp)

# Add the test executable
add_executable(test_main tests/test_main.cpp)
target_link_libraries(test_main engine)
target_include_directories(test_main PRIVATE src/engine)