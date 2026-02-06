cmake_minimum_required(VERSION 3.11)
project(SnakeGame)

set(CMAKE_CXX_STANDARD 17)

# Handle timestamp policy warning
if(POLICY CMP0135)
  cmake_policy(SET CMP0135 NEW)
endif()

# Fetch Raylib 5.5 (More recent release)
include(FetchContent)
FetchContent_Declare(
    raylib
    URL https://github.com/raysan5/raylib/archive/refs/tags/5.5.tar.gz
)
FetchContent_MakeAvailable(raylib)

# Source files
file(GLOB_RECURSE SOURCES "src/*.cpp")

# Executable
add_executable(${PROJECT_NAME} ${SOURCES})

# Link Raylib
target_link_libraries(${PROJECT_NAME} PRIVATE raylib)

# Web compatibility (optional, but good practice with Raylib)
if (PLATFORM_WEB)
    # Custom web build settings would go here
endif()
