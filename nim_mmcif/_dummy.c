#include <Python.h>

static PyMethodDef module_methods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "_dummy",
    "Dummy extension module for triggering build_ext",
    -1,
    module_methods
};

PyMODINIT_FUNC PyInit__dummy(void) {
    return PyModule_Create(&moduledef);
}