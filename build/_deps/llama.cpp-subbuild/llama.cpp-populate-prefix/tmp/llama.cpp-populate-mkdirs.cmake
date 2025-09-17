# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-src")
  file(MAKE_DIRECTORY "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-src")
endif()
file(MAKE_DIRECTORY
  "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-build"
  "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix"
  "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/tmp"
  "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp"
  "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src"
  "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp"
)

set(configSubDirs Debug)
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "C:/Users/Z294FD/Downloads/credential-forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp${cfgdir}") # cfgdir has leading slash
endif()
