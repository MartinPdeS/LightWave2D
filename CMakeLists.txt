cmake_minimum_required(VERSION 3.20..)

set(CMAKE_OSX_DEPLOYMENT_TARGET "15.3" CACHE STRING "Minimum OS X deployment version")

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
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)
find_package(pybind11 CONFIG REQUIRED)

# Platform-specific settings for static linking
if (WIN32)
    message("Windows OS detected")
    set(STATIC_LINK_OPTIONS "-static" "-static-libgcc" "-static-libstdc++")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
    message("AppleClang compiler detected")
    # set(STATIC_LINK_OPTIONS "-static-libstdc++")
elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message("GNU compiler detected")
    # set(STATIC_LINK_OPTIONS "-static-libgcc" "-static-libstdc++")
endif()

message(STATUS "LightWave2D includes directory is: ${LIGHTWAVE2D_CXX_DIR}")
message(STATUS "Python version to be compiled against: ${PYTHON_VERSION}")
message(STATUS "Binary will be installed in location: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")
message(STATUS "Custom flags passed to linker: ${STATIC_LINK_OPTIONS}")

# Create the pybind11 modules
pybind11_add_module(SourceInterface MODULE LightWave2D/cpp/source.cpp)
target_link_options(SourceInterface PUBLIC ${STATIC_LINK_OPTIONS})

pybind11_add_module(fdtd_simulation MODULE LightWave2D/cpp/fdtd_simulation.cpp)
target_link_options(fdtd_simulation PUBLIC ${STATIC_LINK_OPTIONS})


# Ensure position independent code
set_target_properties(SourceInterface fdtd_simulation PROPERTIES POSITION_INDEPENDENT_CODE TRUE)

# Install the modules to the specified directory
install(TARGETS SourceInterface fdtd_simulation DESTINATION "${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")

# Print the installation directory
message(STATUS "Modules will be installed to: ${CMAKE_LIBRARY_OUTPUT_DIRECTORY}")