# cpp/utils/CMakeLists.txt

set(NAME "source")

# Create your library target
add_library("${NAME}" STATIC "${NAME}.cpp")
set_target_properties("${NAME}" PROPERTIES OUTPUT_NAME "${NAME}_core")

# Link with pybind11 module target
target_link_libraries("${NAME}" PRIVATE pybind11::module config field_set)

# Create your Python module
pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
# Separate the Windows import library from the static source library.
set_target_properties("interface_${NAME}" PROPERTIES
    OUTPUT_NAME "${NAME}"
    ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/python-import-libraries"
)
target_link_libraries("interface_${NAME}" PRIVATE "${NAME}")

install(
    TARGETS "interface_${NAME}"
    LIBRARY DESTINATION "LightWave2D"
    RUNTIME DESTINATION "LightWave2D"
)
set_property(GLOBAL APPEND PROPERTY LIGHTWAVE2D_TARGETS "${NAME}")
