# cpp/utils/CMakeLists.txt

set(NAME "source")

# Create your library target
add_library("${NAME}" STATIC "${NAME}.cpp")

# Link with pybind11 module target
target_link_libraries("${NAME}" PRIVATE pybind11::module cpp_config cpp_field_set)

# Create your Python module
pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
set_target_properties("interface_${NAME}" PROPERTIES OUTPUT_NAME "interface_${NAME}")
target_link_libraries("interface_${NAME}" PRIVATE "${NAME}")

set_property(GLOBAL APPEND PROPERTY LIGHTWAVE2D_TARGETS "${NAME}" "interface_${NAME}")
