# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file LICENSE.rst or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION ${CMAKE_VERSION}) # this file comes with cmake

# If CMAKE_DISABLE_SOURCE_CHANGES is set to true and the source directory is an
# existing directory in our source tree, calling file(MAKE_DIRECTORY) on it
# would cause a fatal error, even though it would be a no-op.
if(NOT EXISTS "E:/credential_forge/build/_deps/llama.cpp-src")
  file(MAKE_DIRECTORY "E:/credential_forge/build/_deps/llama.cpp-src")
endif()
file(MAKE_DIRECTORY
  "E:/credential_forge/build/_deps/llama.cpp-build"
  "E:/credential_forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix"
  "E:/credential_forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/tmp"
  "E:/credential_forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp"
  "E:/credential_forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src"
  "E:/credential_forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "E:/credential_forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "E:/credential_forge/build/_deps/llama.cpp-subbuild/llama.cpp-populate-prefix/src/llama.cpp-populate-stamp${cfgdir}") # cfgdir has leading slash
endif()
