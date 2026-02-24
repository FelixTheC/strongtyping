//
// Created by felix on 23.07.20.
//
#define PY_SSIZE_T_CLEAN
#include <Python.h>

long checkTypes(PyObject *obj, PyObject *typeObj);
long unionElementTypes(PyObject *obj, PyObject *typeObj);
long listElementTypes(PyObject *obj, PyObject *typeObj);
long tupleElementTypes(PyObject *obj, PyObject *typeObj);
long setElementTypes(PyObject *originalObj, PyObject *typeObj);
long dictElementTypes(PyObject *obj, PyObject *typeObj);
long checkSubtypes(PyObject *element, PyObject *type, int pyType);
int whichSubtype(PyObject *element);
long unionOrOther(PyObject *type, PyObject *element, int supType);

typedef struct ModuleHelper {
    PyObject* ARGS_TXT;// = PyUnicode_FromString("__args__");
    PyObject* DUNDER_NAME_TXT;// = PyUnicode_FromString("__name__");
    PyObject* NAME_TXT;// = PyUnicode_FromString("_name");
    PyObject* ANNOTATIONS_TXT;// = PyUnicode_FromString("__annotations__");
    PyObject* ORIG_BASES_TXT;// = PyUnicode_FromString("__orig_bases__");
    PyObject* ORIGIN_TXT;// = PyUnicode_FromString("__origin__");
    PyObject* DUNDER_CLASS_TXT;// = PyUnicode_FromString("__class__");
    PyObject* CLASS_TXT;// = PyUnicode_FromString("cls");
    PyObject* IS_TYPEDDICT_TXT;// = PyUnicode_FromString("is_typeddict");

    PyObject* NAME_LIST;// = PyUnicode_FromString("List");
    PyObject* NAME_TUPLE;// = PyUnicode_FromString("Tuple");
    PyObject* NAME_DICT;// = PyUnicode_FromString("Dict");
    PyObject* NAME_TYPED_DICT;// = PyUnicode_FromString("TypedDict");
    PyObject* NAME_SET;// = PyUnicode_FromString("Set");
    PyObject* NAME_LITERAL;// = PyUnicode_FromString("Literal");
    PyObject* NAME_ANY;// = PyUnicode_FromString("Any");
    PyObject* NAME_UNION;// = PyUnicode_FromString("Union");
    PyObject* NAME_ELLIPSIS;// = PyUnicode_FromString("Ellipsis");
    PyObject* NAME_SPECIAL_FORM;// = PyUnicode_FromString("_SpecialForm");
} ModuleHelper;

static ModuleHelper moduleHelper = {0};

static int init_module_helper(void) {
    // Interning is nice here: faster attribute lookups and shared strings.
    moduleHelper.ARGS_TXT = PyUnicode_InternFromString("__args__");
    moduleHelper.DUNDER_NAME_TXT = PyUnicode_InternFromString("__name__");
    moduleHelper.NAME_TXT = PyUnicode_InternFromString("_name");
    moduleHelper.ANNOTATIONS_TXT = PyUnicode_InternFromString("__annotations__");
    moduleHelper.ORIG_BASES_TXT = PyUnicode_InternFromString("__orig_bases__");
    moduleHelper.ORIGIN_TXT = PyUnicode_InternFromString("__origin__");
    moduleHelper.DUNDER_CLASS_TXT = PyUnicode_InternFromString("__class__");
    moduleHelper.CLASS_TXT = PyUnicode_InternFromString("cls");
    moduleHelper.IS_TYPEDDICT_TXT = PyUnicode_InternFromString("is_typeddict");

    moduleHelper.NAME_LIST = PyUnicode_InternFromString("List");
    moduleHelper.NAME_TUPLE = PyUnicode_InternFromString("Tuple");
    moduleHelper.NAME_DICT = PyUnicode_InternFromString("Dict");
    moduleHelper.NAME_TYPED_DICT = PyUnicode_InternFromString("TypedDict");
    moduleHelper.NAME_SET = PyUnicode_InternFromString("Set");
    moduleHelper.NAME_LITERAL = PyUnicode_InternFromString("Literal");
    moduleHelper.NAME_ANY = PyUnicode_InternFromString("Any");
    moduleHelper.NAME_UNION = PyUnicode_InternFromString("Union");
    moduleHelper.NAME_ELLIPSIS = PyUnicode_InternFromString("Ellipsis");
    moduleHelper.NAME_SPECIAL_FORM = PyUnicode_InternFromString("_SpecialForm");

    if (!moduleHelper.ARGS_TXT || !moduleHelper.DUNDER_NAME_TXT || !moduleHelper.NAME_TXT ||
        !moduleHelper.ANNOTATIONS_TXT || !moduleHelper.ORIG_BASES_TXT || !moduleHelper.ORIGIN_TXT ||
        !moduleHelper.DUNDER_CLASS_TXT || !moduleHelper.CLASS_TXT || !moduleHelper.IS_TYPEDDICT_TXT ||
        !moduleHelper.NAME_LIST || !moduleHelper.NAME_TUPLE || !moduleHelper.NAME_DICT ||
        !moduleHelper.NAME_TYPED_DICT || !moduleHelper.NAME_SET || !moduleHelper.NAME_LITERAL ||
        !moduleHelper.NAME_ANY || !moduleHelper.NAME_UNION || !moduleHelper.NAME_ELLIPSIS ||
        !moduleHelper.NAME_SPECIAL_FORM) {
        return -1;
    }
    return 0;
}

static void free_module_helper(void) {
    Py_XDECREF(moduleHelper.ARGS_TXT);
    Py_XDECREF(moduleHelper.DUNDER_NAME_TXT);
    Py_XDECREF(moduleHelper.NAME_TXT);
    Py_XDECREF(moduleHelper.ANNOTATIONS_TXT);
    Py_XDECREF(moduleHelper.ORIG_BASES_TXT);
    Py_XDECREF(moduleHelper.ORIGIN_TXT);
    Py_XDECREF(moduleHelper.DUNDER_CLASS_TXT);
    Py_XDECREF(moduleHelper.CLASS_TXT);
    Py_XDECREF(moduleHelper.IS_TYPEDDICT_TXT);

    Py_XDECREF(moduleHelper.NAME_LIST);
    Py_XDECREF(moduleHelper.NAME_TUPLE);
    Py_XDECREF(moduleHelper.NAME_DICT);
    Py_XDECREF(moduleHelper.NAME_TYPED_DICT);
    Py_XDECREF(moduleHelper.NAME_SET);
    Py_XDECREF(moduleHelper.NAME_LITERAL);
    Py_XDECREF(moduleHelper.NAME_ANY);
    Py_XDECREF(moduleHelper.NAME_UNION);
    Py_XDECREF(moduleHelper.NAME_ELLIPSIS);
    Py_XDECREF(moduleHelper.NAME_SPECIAL_FORM);

    moduleHelper = (ModuleHelper){0};
}

inline int whichSubtype(PyObject *element) {
    // Pointer comparison is O(1). strcmp is O(N).
    if (PyList_Check(element)) return 1;
    if (PyTuple_Check(element)) return 2;
    if (PyDict_Check(element)) return 3;
    if (PySet_Check(element)) return 4;
    return 0;
}

long unionOrOther(PyObject *type, PyObject *element, int supType) {
    PyObject *baseType = PyObject_GetAttr(type, moduleHelper.ORIGIN_TXT);
    long result = 0;

    if (baseType->ob_type->tp_name == moduleHelper.NAME_SPECIAL_FORM) {
        result += unionElementTypes(element, type);
    } else {
        if (supType == 0) {
            return -1;
        } else {
            if (checkSubtypes(element, type, supType) == 0) {
                return 0;
            }
        }
    }
    return result;
}

long checkSubtypes(PyObject *element, PyObject *type, int pyType) {
    /*
     * pyType => 1: list, 2: tuple, 3: dict, 4: set
     */
    PyObject *baseType = PyObject_GetAttr(type, moduleHelper.ORIGIN_TXT);

    if (pyType == 1 && PyObject_IsInstance(element, baseType) == 1) {
        PyObject *supTypes = PyObject_GetAttr(type, moduleHelper.ARGS_TXT);
        long result = 0;
        long supTypeSize = PyObject_Length(supTypes);
        for (int x = 0; x < supTypeSize; x++) {
            PyObject *supType = PyTuple_GetItem(supTypes, x);
            long recursiveResult = listElementTypes(element, supType);
            result += recursiveResult;
        }
        return result >= supTypeSize;
    } else if (pyType == 2 && PyObject_IsInstance(element, baseType) == 1) {
        PyObject *supTypes = PyObject_GetAttr(type, moduleHelper.ARGS_TXT);
        long result = 0;
        long supTypeSize = PyObject_Length(supTypes);
        for (int x = 0; x < supTypeSize; x++) {
            PyObject *supType = PyTuple_GetItem(supTypes, x);
            long recursiveResult = tupleElementTypes(element, supType);
            result += recursiveResult;
        }
        return result >= supTypeSize;
    } else if (pyType == 3 && PyObject_IsInstance(element, baseType) == 1) {
        PyObject *supTypes = PyObject_GetAttr(type, moduleHelper.ARGS_TXT);
        long result = 0;
        long supTypeSize = PyObject_Length(supTypes);
        for (int x = 0; x < supTypeSize; x++) {
            PyObject *supType = PyTuple_GetItem(supTypes, x);
            long recursiveResult = dictElementTypes(element, supType);
            result += recursiveResult;
        }
        return result >= supTypeSize;
    } else if (pyType == 4 && PyObject_IsInstance(element, baseType) == 1) {
        PyObject *supTypes = PyObject_GetAttr(type, moduleHelper.ARGS_TXT);
        long result = 0;
        long supTypeSize = PyObject_Length(supTypes);
        for (int x = 0; x < supTypeSize; x++) {
            PyObject *supType = PyTuple_GetItem(supTypes, x);
            long recursiveResult = setElementTypes(element, supType);
            result += recursiveResult;
        }
        return result >= supTypeSize;
    } else {
        return PyObject_IsInstance(element, baseType);
    }
}

long unionElementTypes(PyObject *obj, PyObject *typeObj) {
    long ttype = 0;
    long result = 0;
    ttype = whichSubtype(obj);

    PyObject *typeArgs = PyObject_GetAttr(typeObj, moduleHelper.ARGS_TXT);
    long typeArgSize = PyObject_Length(typeArgs);

    for (int i = 0; i < typeArgSize; i++) {
        PyObject *typeArg = PyTuple_GetItem(typeArgs, i);

        if (PyObject_HasAttr(typeArg, moduleHelper.ARGS_TXT) == 0 && ttype == 0) {
            result += PyObject_IsInstance(obj, typeArg);
        } else if (PyObject_HasAttr(typeArg, moduleHelper.ORIGIN_TXT)) {

            PyObject *baseType = PyObject_GetAttr(typeArg, moduleHelper.ORIGIN_TXT);

            if (baseType == NULL) {
                baseType = typeArg;
            }

            if (ttype == 1 && PyObject_IsInstance(obj, baseType) == 1) {
                long recursiveResult = listElementTypes(obj, typeArg);
                result += recursiveResult;
            } else if (ttype == 2 && PyObject_IsInstance(obj, baseType) == 1) {
                long recursiveResult = tupleElementTypes(obj, typeArg);
                result += recursiveResult;
            } else if (ttype == 3 && PyObject_IsInstance(obj, baseType) == 1) {
                long recursiveResult = dictElementTypes(obj, typeArg);
                result += recursiveResult;
            } else if (ttype == 4 && PyObject_IsInstance(obj, baseType) == 1) {
                long recursiveResult = setElementTypes(obj, typeArg);
                result += recursiveResult;
            }
        } else {
            result += PyObject_IsInstance(obj, typeArg);
        }
    }
    return result;
}


long setElementTypes(PyObject *originalObj, PyObject *typeObj) {
    long objSize = PySet_Size(originalObj);
    PyObject *test_obj = PySet_New(originalObj);

    if (PyObject_HasAttr(typeObj, moduleHelper.ARGS_TXT)) {
        PyObject *typeArgs = PyObject_GetAttr(typeObj, moduleHelper.ARGS_TXT);
        PyObject *baseType = PyObject_GetAttr(typeObj, moduleHelper.ORIGIN_TXT);

        if (PyObject_IsInstance(test_obj, baseType) == 1) {
            long typeArgSize = PyObject_Length(typeArgs);
            long result = 0;

            for (int i = 0; i < objSize; i++) {
                int supType = 0;
                PyObject *setElement = PySet_Pop(test_obj);

                supType = whichSubtype(setElement);

                for (int j = 0; j < typeArgSize; j++) {
                    PyObject *type = PyTuple_GetItem(typeArgs, j);


                    if (PyObject_HasAttr(type, moduleHelper.ARGS_TXT)) {
                        if (unionOrOther(type, setElement, supType) < 1) {
                            return 0;
                        } else {
                            continue;
                        }
                    } else if (PyObject_HasAttr(type, moduleHelper.NAME_TXT)) {
                        PyObject *_name = PyObject_GetAttr(type, moduleHelper.NAME_TXT);
                        if (_name->ob_type->tp_name = moduleHelper.NAME_ANY) {
                            return 1;
                        }
                    } else {
                        if (PyObject_IsInstance(setElement, type) <= 1) {
                          return 0;
                        }
                    }
                }
            }
            return result >= objSize;

        } else {
            return checkTypes(originalObj, typeObj);
        }
    }
}


long dictElementTypes(PyObject *obj, PyObject *typeObj) {
    long objSize = PyDict_Size(obj);

		PyObject *typeArgs = PyObject_GetAttr(typeObj, moduleHelper.ARGS_TXT);

    if (typeArgs != NULL) {

        PyObject *keyTypes = PyTuple_GetItem(typeArgs, 0);
        PyObject *valueTypes = PyTuple_GetItem(typeArgs, 1);

        PyObject *objItems = PyDict_Items(obj);

        long result = 0;

        for (int i = 0; i < objSize; i++) {
            PyObject *objItem = PyList_GetItem(objItems, i);
            PyObject *key = PyTuple_GetItem(objItem, 0);
            PyObject *value = PyTuple_GetItem(objItem, 1);


            if (PyObject_HasAttr(keyTypes, moduleHelper.ARGS_TXT)) {
                int supType = whichSubtype(key);

                long tmp = unionOrOther(keyTypes, key, supType);

                if (tmp < 1) {
                    return 0;
                } else {
                    continue;
                }

            } else if (PyObject_HasAttr(valueTypes, moduleHelper.NAME_TXT)) {
                PyObject *_name = PyObject_GetAttr(keyTypes, moduleHelper.NAME_TXT);
                if (_name->ob_type->tp_name == moduleHelper.NAME_ANY) {
                    return 1;
                }
            } else {
                if (PyObject_IsInstance(key, keyTypes) == 0) return 0;
            }

            if (PyObject_HasAttr(valueTypes, moduleHelper.ARGS_TXT)) {
                int supType = whichSubtype(value);
                long tmp = unionOrOther(valueTypes, value, supType);
                if (tmp < 1) {
                    return 0;
                } else {
                    continue;
                }

            } else if (PyObject_HasAttr(valueTypes, moduleHelper.NAME_TXT)) {
                PyObject *_name = PyObject_GetAttr(valueTypes, moduleHelper.NAME_TXT);
                if (_name->ob_type->tp_name == moduleHelper.NAME_ANY) {
                    return 1;
                }
            } else {
                if (PyObject_IsInstance(value, valueTypes) == 0) return 0;
            }
        }
        if (result >= objSize) {
            return 1;
        } else {
            return 0;
        }

    } else {
        return checkTypes(obj, typeObj);
    }
}

long tupleElementTypes(PyObject *obj, PyObject *typeObj) {
    long objSize = PyObject_Length(obj);

    if (PyObject_HasAttrString(typeObj, "__args__")) {

        PyObject *typeArgs = PyObject_GetAttrString(typeObj, "__args__");
        PyObject *baseType = PyObject_GetAttrString(typeObj, "__origin__");
        long typeArgSize = PyObject_Length(typeArgs);

        if ((PyObject_IsInstance(obj, baseType) == 1) && (objSize == typeArgSize)) {
            long result;

            for (int i = 0; i < objSize; i++) {
                int supType = 0;

                PyObject *tupleElement = PyTuple_GetItem(obj, i);
                PyObject *tupleElementType = PyTuple_GetItem(typeArgs, i);

                supType = whichSubtype(tupleElement);

                if (PyObject_HasAttrString(tupleElementType, "__args__")) {

                    long tmp = unionOrOther(tupleElement, tupleElementType, supType);
                    if (tmp > 1) {
                        result += tmp;
                    } else if (tmp == 0) {
                        return 0;
                    } else {
                        continue;
                    }

                } else if (PyObject_HasAttrString(tupleElementType, "_name")) {
                    PyObject *_name = PyObject_GetAttrString(tupleElementType, "_name");
                    if (strcmp(_name->ob_type->tp_name, "Any") == 0) {
                        return 1;
                    }
                } else {
                    if (PyObject_IsInstance(tupleElement, tupleElementType) == 0) {
                        return 0;
                    }
                }
            }
            return result >= objSize;
        } else {
            return 0;
        }

    } else {
        return checkTypes(obj, typeObj);
    }
}

long listElementTypes(PyObject *obj, PyObject *typeObj) {
    long objSize = PyObject_Length(obj);

    if (PyObject_HasAttrString(typeObj, "__args__")) {

        PyObject *typeArgs = PyObject_GetAttrString(typeObj, "__args__");
        long typeArgSize = PyObject_Length(typeArgs);

        long result = 0;
        for(int i = 0; i < objSize; i++) {

            PyObject *listElem = obj->ob_type->tp_as_sequence->sq_item(obj, i);

            int supType = whichSubtype(listElem);

            for(int j = 0; j < typeArgSize; j++) {
                PyObject *type = PyTuple_GetItem(typeArgs, j);

                if (PyObject_HasAttrString(type, "__args__")) {
                    long tmp = unionOrOther(type, listElem, supType);
                    if (tmp > 1) {
                        result += tmp;
                    } else if (tmp == 0) {
                        return 0;
                    } else {
                        continue;
                    }

                } else if (PyObject_HasAttrString(type, "_name")) {
                    PyObject *_name = PyObject_GetAttrString(type, "_name");
                    if (strcmp(_name->ob_type->tp_name, "Any") == 0) {
                        return 1;
                    }
                } else {
                    result += PyObject_IsInstance(listElem, type);
                }
            }
        }
        return result >= objSize;

    } else {
        return checkTypes(obj, typeObj);
    }
}


long checkTypes(PyObject *obj, PyObject *typeObj) {
    long objSize = PyObject_Length(obj);

    if (objSize > 1) {
        long result = 0;
        if (PyObject_IsInstance(obj, typeObj) == 1) {
            return 1;
        }
        for(int i = 0; i < objSize; i++) {
            PyObject *listElem = obj->ob_type->tp_as_sequence->sq_item(obj, i);
            if (PyObject_IsInstance(listElem, typeObj) == 0)
                break;
            else {
                result++;
            }
        }
        // 0 means False
        return result >= objSize;
    } else {
        return PyObject_IsInstance(obj, typeObj);
    }
}


static PyObject* sttyping_stlist_instance(PyObject *self, PyObject *args) {

    static PyObject *obj;
    static PyObject *typeObj;

    // https://docs.python.org/3/c-api/arg.html
    if (!PyArg_ParseTuple(args, "OO", &obj, &typeObj))
        return NULL;

    return PyBool_FromLong(listElementTypes(obj, typeObj));
}

static PyObject* sttyping_sttuple_instance(PyObject *self, PyObject *args) {

    static PyObject *obj;
    static PyObject *typeObj;

    if (!PyArg_ParseTuple(args, "OO", &obj, &typeObj))
        return NULL;

    return PyBool_FromLong(tupleElementTypes(obj, typeObj));
}

static PyObject* sttyping_stdict_instance(PyObject *self, PyObject *args) {

    static PyObject *obj;
    static PyObject *typeObj;

    if (!PyArg_ParseTuple(args, "OO", &obj, &typeObj))
        return NULL;

    return PyBool_FromLong(dictElementTypes(obj, typeObj));
}

static PyObject* sttyping_stset_instance(PyObject *self, PyObject *args) {

    static PyObject *obj;
    static PyObject *typeObj;

    if (!PyArg_ParseTuple(args, "OO", &obj, &typeObj))
        return NULL;

    return PyBool_FromLong(setElementTypes(obj, typeObj));
}

static PyMethodDef SttypingMethods[] = {
        {"st_list",  sttyping_stlist_instance, METH_VARARGS,"Type checking for list elements."},
        {"st_tuple",  sttyping_sttuple_instance, METH_VARARGS,"Type checking for tuple elements."},
        {"st_dict",  sttyping_stdict_instance, METH_VARARGS,"Type checking for dict items."},
        {"st_set",  sttyping_stset_instance, METH_VARARGS,"Type checking for set elements."},
        {NULL, NULL, 0, NULL}
};

static void sttyping_free(void *m) {
    (void)m;
    free_module_helper();
}

static struct PyModuleDef sttypingmodule = {
        PyModuleDef_HEAD_INIT,
        "sttyping",   /* name of module */
        "Instance checks only for specific types. Submodule for strongtyping.", /* module documentation, may be NULL */
        -1,       /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
        SttypingMethods,
        NULL,
        NULL,
        NULL,
        sttyping_free
};

PyMODINIT_FUNC PyInit_sttyping(void) {
    if (init_module_helper() < 0) {
        free_module_helper();
        return NULL;
    }

    PyObject *m = PyModule_Create(&sttypingmodule);
    if (!m) {
        free_module_helper();
        return NULL;
    }
    return m;
}