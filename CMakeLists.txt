cmake_minimum_required(VERSION 3.16)

project(scrabble_solver CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Add the engine library
add_library(engine src/engine/engine.cpp)

# Create a simple test executable without Google Test for now
add_executable(simple_test tests/simple_test.cpp)
target_link_libraries(simple_test engine)
target_include_directories(simple_test PRIVATE src/engine)