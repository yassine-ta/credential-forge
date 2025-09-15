cmake_minimum_required(VERSION 3.16)
project(CredentialForge)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Set build type
if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

# Compiler-specific options
if(MSVC)
    add_compile_options(/W4 /O2)
    add_compile_definitions(_CRT_SECURE_NO_WARNINGS)
else()
    add_compile_options(-Wall -Wextra -O3)
endif()

# Find required packages (PkgConfig is optional on Windows)
if(NOT WIN32)
    find_package(PkgConfig REQUIRED)
endif()

# Python development headers
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Threading support
find_package(Threads REQUIRED)

# OpenSSL for cryptographic functions (optional)
find_package(OpenSSL QUIET)
if(NOT OpenSSL_FOUND)
    message(WARNING "OpenSSL not found - some cryptographic features may be disabled")
endif()

# Fetch llama.cpp as external dependency
include(FetchContent)

FetchContent_Declare(
    llama.cpp
    GIT_REPOSITORY https://github.com/ggerganov/llama.cpp.git
    GIT_TAG master
    GIT_SHALLOW TRUE
)

# Configure llama.cpp build options
set(LLAMA_NATIVE OFF CACHE BOOL "Enable native CPU optimizations")
set(LLAMA_AVX ON CACHE BOOL "Enable AVX instructions")
set(LLAMA_AVX2 ON CACHE BOOL "Enable AVX2 instructions")
set(LLAMA_FMA ON CACHE BOOL "Enable FMA instructions")
set(LLAMA_F16C ON CACHE BOOL "Enable F16C instructions")
set(LLAMA_SSE3 ON CACHE BOOL "Enable SSE3 instructions")
set(LLAMA_SSSE3 ON CACHE BOOL "Enable SSSE3 instructions")
set(LLAMA_SSE4_1 ON CACHE BOOL "Enable SSE4.1 instructions")
set(LLAMA_SSE4_2 ON CACHE BOOL "Enable SSE4.2 instructions")
set(LLAMA_POPCNT ON CACHE BOOL "Enable POPCNT instruction")

# Disable CUDA and other GPU backends
set(LLAMA_CUDA OFF CACHE BOOL "Disable CUDA support")
set(LLAMA_METAL OFF CACHE BOOL "Disable Metal support")
set(LLAMA_VULKAN OFF CACHE BOOL "Disable Vulkan support")
set(LLAMA_OPENCL OFF CACHE BOOL "Disable OpenCL support")
set(LLAMA_HIPBLAS OFF CACHE BOOL "Disable HIP support")
set(LLAMA_CLBLAST OFF CACHE BOOL "Disable CLBlast support")

# Enable CPU optimizations (platform-specific)
if(APPLE)
    set(LLAMA_ACCELERATE ON CACHE BOOL "Enable Accelerate framework (macOS)")
endif()
if(NOT WIN32)
    set(LLAMA_BLAS ON CACHE BOOL "Enable BLAS support")
    set(LLAMA_LAPACK ON CACHE BOOL "Enable LAPACK support")
endif()

# Build llama.cpp
FetchContent_MakeAvailable(llama.cpp)

# Include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/src)
include_directories(${Python3_INCLUDE_DIRS})
include_directories(${llama.cpp_SOURCE_DIR})
include_directories(${llama.cpp_BINARY_DIR})

# Source files for native components
set(NATIVE_SOURCES
    src/credential_utils.cpp
    src/llama_cpp_interface.cpp
    src/cpu_optimizer.cpp
    src/memory_manager.cpp
    src/parallel_executor.cpp
)

# Create shared library for Python extension
add_library(credentialforge_native SHARED ${NATIVE_SOURCES})

# Link libraries
target_link_libraries(credentialforge_native 
    ${Python3_LIBRARIES}
    Threads::Threads
    llama
)

# Link OpenSSL if available
if(OpenSSL_FOUND)
    target_link_libraries(credentialforge_native 
        OpenSSL::SSL
        OpenSSL::Crypto
    )
endif()

# Set compile definitions for CPU optimization (platform-specific)
target_compile_definitions(credentialforge_native PRIVATE
    GGML_USE_F16C
    GGML_USE_FMA
    GGML_USE_AVX
    GGML_USE_AVX2
    GGML_USE_SSE3
    GGML_USE_SSSE3
    GGML_USE_SSE4_1
    GGML_USE_SSE4_2
    GGML_USE_POPCNT
)

# Platform-specific definitions
if(APPLE)
    target_compile_definitions(credentialforge_native PRIVATE GGML_USE_ACCELERATE)
endif()
if(NOT WIN32)
    target_compile_definitions(credentialforge_native PRIVATE 
        GGML_USE_OPENBLAS
        GGML_USE_CBLAS
    )
endif()

# Set output directory
set_target_properties(credentialforge_native PROPERTIES
    LIBRARY_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/credentialforge/native
    RUNTIME_OUTPUT_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}/credentialforge/native
)

# Install targets
install(TARGETS credentialforge_native
    LIBRARY DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/credentialforge/native
    RUNTIME DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/credentialforge/native
)

# Custom target for building Python wheel
add_custom_target(build_wheel
    COMMAND ${Python3_EXECUTABLE} -m pip install build wheel
    COMMAND ${Python3_EXECUTABLE} -m build
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    COMMENT "Building Python wheel package"
)

# Custom target for running tests
add_custom_target(run_tests
    COMMAND ${Python3_EXECUTABLE} -m pytest tests/ -v
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    DEPENDS credentialforge_native
    COMMENT "Running test suite"
)

# Performance optimization flags
if(CMAKE_BUILD_TYPE STREQUAL "Release")
    if(MSVC)
        target_compile_options(credentialforge_native PRIVATE /O2 /DNDEBUG)
    else()
        target_compile_options(credentialforge_native PRIVATE -O3 -DNDEBUG -march=native)
    endif()
endif()

# Debug flags
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    if(MSVC)
        target_compile_options(credentialforge_native PRIVATE /Od /Zi /DDEBUG)
    else()
        target_compile_options(credentialforge_native PRIVATE -g -O0 -DDEBUG)
    endif()
endif()

# Print configuration summary
message(STATUS "Build type: ${CMAKE_BUILD_TYPE}")
message(STATUS "Python executable: ${Python3_EXECUTABLE}")
message(STATUS "Python version: ${Python3_VERSION}")
message(STATUS "Python include dirs: ${Python3_INCLUDE_DIRS}")
message(STATUS "Python libraries: ${Python3_LIBRARIES}")
