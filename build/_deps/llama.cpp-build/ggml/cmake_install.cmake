# Install script for directory: E:/credential_forge/build/_deps/llama.cpp-src/ggml

# Set the install prefix
if(NOT DEFINED CMAKE_INSTALL_PREFIX)
  set(CMAKE_INSTALL_PREFIX "C:/Program Files (x86)/CredentialForge")
endif()
string(REGEX REPLACE "/$" "" CMAKE_INSTALL_PREFIX "${CMAKE_INSTALL_PREFIX}")

# Set the install configuration name.
if(NOT DEFINED CMAKE_INSTALL_CONFIG_NAME)
  if(BUILD_TYPE)
    string(REGEX REPLACE "^[^A-Za-z0-9_]+" ""
           CMAKE_INSTALL_CONFIG_NAME "${BUILD_TYPE}")
  else()
    set(CMAKE_INSTALL_CONFIG_NAME "Release")
  endif()
  message(STATUS "Install configuration: \"${CMAKE_INSTALL_CONFIG_NAME}\"")
endif()

# Set the component getting installed.
if(NOT CMAKE_INSTALL_COMPONENT)
  if(COMPONENT)
    message(STATUS "Install component: \"${COMPONENT}\"")
    set(CMAKE_INSTALL_COMPONENT "${COMPONENT}")
  else()
    set(CMAKE_INSTALL_COMPONENT)
  endif()
endif()

# Is this installation the result of a crosscompile?
if(NOT DEFINED CMAKE_CROSSCOMPILING)
  set(CMAKE_CROSSCOMPILING "FALSE")
endif()

# Set path to fallback-tool for dependency-resolution.
if(NOT DEFINED CMAKE_OBJDUMP)
  set(CMAKE_OBJDUMP "E:/credential_forge/mingw64/bin/objdump.exe")
endif()

if(NOT CMAKE_INSTALL_LOCAL_ONLY)
  # Include the install script for the subdirectory.
  include("E:/credential_forge/build/_deps/llama.cpp-build/ggml/src/cmake_install.cmake")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/credential_forge/build/_deps/llama.cpp-build/ggml/src/ggml.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/include" TYPE FILE FILES
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-cpu.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-alloc.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-backend.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-blas.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-cann.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-cpp.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-cuda.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-opt.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-metal.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-rpc.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-sycl.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-vulkan.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/ggml-webgpu.h"
    "E:/credential_forge/build/_deps/llama.cpp-src/ggml/include/gguf.h"
    )
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib" TYPE STATIC_LIBRARY FILES "E:/credential_forge/build/_deps/llama.cpp-build/ggml/src/ggml-base.a")
endif()

if(CMAKE_INSTALL_COMPONENT STREQUAL "Unspecified" OR NOT CMAKE_INSTALL_COMPONENT)
  file(INSTALL DESTINATION "${CMAKE_INSTALL_PREFIX}/lib/cmake/ggml" TYPE FILE FILES
    "E:/credential_forge/build/_deps/llama.cpp-build/ggml/ggml-config.cmake"
    "E:/credential_forge/build/_deps/llama.cpp-build/ggml/ggml-version.cmake"
    )
endif()

string(REPLACE ";" "\n" CMAKE_INSTALL_MANIFEST_CONTENT
       "${CMAKE_INSTALL_MANIFEST_FILES}")
if(CMAKE_INSTALL_LOCAL_ONLY)
  file(WRITE "E:/credential_forge/build/_deps/llama.cpp-build/ggml/install_local_manifest.txt"
     "${CMAKE_INSTALL_MANIFEST_CONTENT}")
endif()
