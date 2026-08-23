set(NAME "grid")

add_library("${NAME}" STATIC grid.cpp)
set_target_properties("${NAME}" PROPERTIES OUTPUT_NAME "${NAME}_core")
target_link_libraries("${NAME}" PRIVATE pybind11::module)

pybind11_add_module("interface_${NAME}" MODULE interface.cpp)
# On Windows a MODULE target creates an import ``.lib`` file.  Keep it out of
# this directory so it cannot overwrite the static ``grid.lib`` dependency.
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
