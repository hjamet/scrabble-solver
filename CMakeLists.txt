cmake_minimum_required(VERSION 3.16)

project(scrabble_solver C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Add the engine library
add_library(engine src/engine/engine.c)

# Add the test executable
add_executable(test_main tests/test_main.c)
target_link_libraries(test_main engine)