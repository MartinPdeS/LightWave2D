# --------------------- CMake configuration --------------------
cmake_minimum_required(VERSION 3.20)
set(CMAKE_OSX_DEPLOYMENT_TARGET "15.0" CACHE STRING "Minimum OS X deployment version")
project(LightWave2D CXX)

# CMake settings
set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Type of build")
# --------------------- CMake configuration --------------------

# --------------------- Set the output directory for libraries --------------------
set(LOCAL_CXX_DIR "${PROJECT_NAME}/cpp")
set(LOCAL_BIN_DIR "${CMAKE_SOURCE_DIR}/${PROJECT_NAME}/binary")
# --------------------- Set the output directory for libraries --------------------

# --------------------- Platform-specific compiler and linker options --------------------
if(APPLE AND CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
    set(OpenMP_CXX_FLAGS "-Xpreprocessor -fopenmp" CACHE STRING "")
    set(OpenMP_CXX_LIB_NAMES "omp" CACHE STRING "")
    find_library(OpenMP_omp_LIBRARY omp HINTS $ENV{LIBOMP_PREFIX}/lib /opt/homebrew/opt/libomp/lib /usr/local/opt/libomp/lib)
    if(OpenMP_omp_LIBRARY)
        set(OpenMP_CXX_LIBRARIES "${OpenMP_omp_LIBRARY}" CACHE STRING "")
    endif()
endif()

# Platform-specific settings for static linking
if (WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message("MinGW detected on Windows")
    set(STATIC_LINK_OPTIONS "-static")
    add_compile_options(-fopenmp)
    add_link_options(-static -fopenmp -Wl,--whole-archive -lgomp -Wl,--no-whole-archive)
endif()

if (WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    add_compile_options(/W4 /permissive- /Zc:preprocessor)
else()
    add_compile_options(-Wall -Wextra -pedantic-errors)
endif()
# --------------------- Platform-specific compiler and linker options --------------------


# --------------------- Find dependencies and compile options --------------------
# Include directories
find_package(OpenMP REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)
# --------------------- Find dependencies and compile options --------------------

# ----------------- Package specific settings--------------------

# ----------------- Package specific settings--------------------

# ----------------- logging build configuration --------------------
message(STATUS "")
message(STATUS "==================== Build configuration ====================")

message(STATUS "Compiler information")
message(STATUS "  C compiler           : ${CMAKE_C_COMPILER}")
message(STATUS "  C compiler ID        : ${CMAKE_C_COMPILER_ID}")
message(STATUS "  C compiler version   : ${CMAKE_C_COMPILER_VERSION}")

message(STATUS "  CXX compiler         : ${CMAKE_CXX_COMPILER}")
message(STATUS "  CXX compiler ID      : ${CMAKE_CXX_COMPILER_ID}")
message(STATUS "  CXX compiler version : ${CMAKE_CXX_COMPILER_VERSION}")

message(STATUS "  Fortran compiler     : ${CMAKE_Fortran_COMPILER}")
message(STATUS "  Fortran ID           : ${CMAKE_Fortran_COMPILER_ID}")
message(STATUS "  Fortran version      : ${CMAKE_Fortran_COMPILER_VERSION}")

message(STATUS "")
message(STATUS "OpenMP configuration")
message(STATUS "  OpenMP flags         : ${OpenMP_CXX_FLAGS}")
message(STATUS "  OpenMP detected      : ${OpenMP_FOUND}")
message(STATUS "  OpenMP version       : ${OpenMP_CXX_VERSION}")

message(STATUS "")
message(STATUS "Python configuration")
message(STATUS "  Python executable    : ${Python_EXECUTABLE}")
message(STATUS "  Python version       : ${PYBIND11_PYTHON_VERSION}")
message(STATUS "  Python include dir   : ${Python_INCLUDE_DIRS}")
message(STATUS "  Python site packages : ${Python_SITELIB}")

message(STATUS "")
message(STATUS "PyMieSim integration")
message(STATUS "  PyMieSim version     : ${PACKAGE_VERSION}")
message(STATUS "  PyMieSim include dir : ${LOCAL_CXX_DIR}")

message(STATUS "")
message(STATUS "Install destination")
message(STATUS "  Binary output path   : ${LOCAL_BIN_DIR}")

message(STATUS "==============================================================")
message(STATUS "")
# ----------------- logging build configuration --------------------


# ----------------- collect subdirectories --------------------
add_subdirectory(LightWave2D/cpp/config)         # config
add_subdirectory(LightWave2D/cpp/field_set)      # field_set
add_subdirectory(LightWave2D/cpp/mesh_set)       # mesh_set
add_subdirectory(LightWave2D/cpp/source)         # source
add_subdirectory(LightWave2D/cpp/simulator)         # simulator
# ----------------- collect subdirectories --------------------

install(
    TARGETS ${LIGHTWAVE2D_TARGETS}
    LIBRARY DESTINATION ${LOCAL_BIN_DIR}
    ARCHIVE DESTINATION ${LOCAL_BIN_DIR}
    RUNTIME DESTINATION ${LOCAL_BIN_DIR}
)
