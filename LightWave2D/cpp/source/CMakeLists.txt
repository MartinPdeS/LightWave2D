# cpp/utils/CMakeLists.txt

set(NAME "source")

# Create your library target
add_library("cpp_${NAME}" STATIC "${NAME}.cpp")

# Link with pybind11 module target
target_link_libraries("cpp_${NAME}" PRIVATE pybind11::module cpp_config cpp_field_set)

# Create your Python module
pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
set_target_properties("interface_${NAME}" PROPERTIES OUTPUT_NAME "interface_${NAME}")
target_link_libraries("interface_${NAME}" PRIVATE "cpp_${NAME}")

install(
    TARGETS cpp_${NAME} interface_${NAME}
    LIBRARY DESTINATION ${LOCAL_BIN_DIR}
    ARCHIVE DESTINATION ${LOCAL_BIN_DIR}
    RUNTIME DESTINATION ${LOCAL_BIN_DIR}
)