cmake_minimum_required(VERSION 3.20)

set(CMAKE_OSX_DEPLOYMENT_TARGET "14.0" CACHE STRING "Minimum OS X deployment version")

project(LightWave2D LANGUAGES CXX)

set(CMAKE_VERBOSE_MAKEFILE ON)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_STANDARD 17)
set(LIGHTWAVE2D_CXX_DIR "LightWave2D/cpp")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/LightWave2D/binary")
set(CMAKE_BUILD_TYPE "Release" CACHE STRING "Type of build" FORCE)


# Ensure -fPIC is used globally
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
add_compile_options(-fPIC)

#FIND_PACKAGE------------------------
find_package(OpenMP REQUIRED)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Platform-specific settings for static linking
if (WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message("MinGW detected on Windows")
    set(STATIC_LINK_OPTIONS "-static")
    add_compile_options(-fopenmp)
    add_link_options(-static -fopenmp -Wl,--whole-archive -lgomp -Wl,--no-whole-archive)
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
    message("AppleClang compiler detected")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message("GNU compiler detected")
endif()

message(STATUS "LightWave2D includes directory is: ${LIGHTWAVE2D_CXX_DIR}")
message(STATUS "Python version to be compiled against: ${PYTHON_VERSION}")
message(STATUS "Binary will be installed in location: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "Custom flags passed to linker: ${STATIC_LINK_OPTIONS}")


# Function to add pybind11 modules with an optional library to link
function(add_lightwave2d_module name source optional_lib)
    # Add the pybind11 module
    pybind11_add_module(${name} MODULE "${LIGHTWAVE2D_CXX_DIR}/${source}")

    # Set target properties
    set_target_properties(${name} PROPERTIES OUTPUT_NAME ${name})
    set_target_properties(${name} PROPERTIES POSITION_INDEPENDENT_CODE TRUE)

    # Link options
    target_link_options(${name} PUBLIC ${STATIC_LINK_OPTIONS})

    # Check if an optional library is provided and link it
    if(NOT "${optional_lib}" STREQUAL "")
        target_link_libraries(${name} PRIVATE ${optional_lib})
    endif()
endfunction()


add_lightwave2d_module(SourceInterface "source.cpp" "")
add_lightwave2d_module(fdtd_simulation "fdtd_simulation.cpp" OpenMP::OpenMP_CXX)


# Special handling for Experiment module
if (WIN32 AND CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    add_link_options(-static -fopenmp -Wl,--whole-archive -lgomp -Wl,--no-whole-archive)
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_link_libraries(fdtd_simulation PRIVATE OpenMP::OpenMP_CXX)
else()
    target_link_libraries(fdtd_simulation PRIVATE "-Xpreprocessor -fopenmp")
endif()


# Print the installation directory
message(STATUS "Modules will be installed to: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
