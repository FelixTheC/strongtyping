# cython: language_level=3, boundscheck=False, wraparound=False, cdivision=True
# use only for debugging
# from __future__ import print_function

from cpython.exc cimport PyErr_Occurred
from cpython.tuple cimport PyTuple_GetItem, PyTuple_Pack, PyTuple_Size, PyTuple_New, PyTuple_SetItem, PyTuple_Check
from cpython.list cimport PyList_GetItem
from cpython.dict cimport PyDict_Check, PyDict_Next, PyDict_Size, PyDict_Keys
from cpython.unicode cimport PyUnicode_AsUTF8, PyUnicode_InternFromString, PyUnicode_Check
from cpython.ref cimport PyObject, PyTypeObject, Py_XDECREF
from cpython.object cimport PyObject_TypeCheck, PyObject_GetAttr, PyObject_RichCompareBool, PyObject_Str, Py_TYPE

cdef extern from "Python.h":
    PyObject* PyObject_GetAttrString(PyObject* obj, const char* attr_name)
    PyObject* PyObject_GetAttr(PyObject* obj, PyObject* attr_name)
    PyObject* PyUnicode_InternFromString(const char *v)
    int PyObject_HasAttrString(PyObject* obj, const char* attr_name)
    void Py_XDECREF(PyObject* obj)
    bint PyObject_TypeCheck(PyObject* o, PyTypeObject *type)
    const char *PyUnicode_AsUTF8(PyObject* unicode) except NULL
    bint PyDict_Check(PyObject* p)
    Py_ssize_t PyDict_Size(PyObject* p) except -1
    void PyErr_Clear()
    PyObject * PyTuple_GetItem(PyObject*  p, Py_ssize_t pos) except NULL
    int PyDict_Next(PyObject* p, Py_ssize_t *ppos, PyObject * *pkey, PyObject * *pvalue)
    bint PyObject_RichCompareBool(PyObject* o1, PyObject* o2, int opid) except -1
    PyObject* PyObject_GetIter(PyObject* o)
    PyObject * PyIter_Next(PyObject * iter)
    Py_ssize_t PyObject_Length(PyObject* o) except -1
    PyObject* PyDict_Keys(PyObject* p) # returns list as new reference
    PyObject * PyDict_GetItem(PyObject* p, PyObject* key)
    PyObject* PyList_GetItem(PyObject* list, Py_ssize_t index) except NULL
    object PyObject_Str(PyObject* o)
    cdef PyTypeObject *Py_TYPE(PyObject*)
    bint PyTuple_Check(PyObject*  p)
    bint PyList_Check(PyObject*  p)
    bint PySet_Check(PyObject*  p)
    bint PyFrozenSet_Check(PyObject*  p)
    bint PyLong_Check(PyObject*  p)
    bint PyFloat_Check(PyObject*  p)
    bint PyUnicode_Check(PyObject*  p)


cdef int not_supported = -999

cdef PyObject * ARGS_TXT = PyUnicode_InternFromString("__args__")
cdef PyObject * DUNDER_NAME_TXT = PyUnicode_InternFromString("__name__")
cdef PyObject * NAME_TXT = PyUnicode_InternFromString("_name")
cdef PyObject * ANNOTATIONS_TXT = PyUnicode_InternFromString("__annotations__")
cdef PyObject * ORIG_BASES_TXT = PyUnicode_InternFromString("__orig_bases__")
cdef PyObject * ORIGIN_TXT = PyUnicode_InternFromString("__origin__")
cdef PyObject * DUNDER_CLASS_TXT = PyUnicode_InternFromString("__class__")
cdef PyObject * CLASS_TXT = PyUnicode_InternFromString("cls")
cdef PyObject * IS_TYPEDDICT_TXT = PyUnicode_InternFromString("is_typeddict")

cdef enum TypeID:
    TYPE_UNKNOWN = 0
    TYPE_UNION = 1
    TYPE_ANY = 2
    TYPE_LIST = 3
    TYPE_DICT = 4
    TYPE_TUPLE = 5
    TYPE_SET = 6
    TYPE_FROZENSET = 7
    TYPE_INT = 8
    TYPE_FLOAT = 9
    TYPE_BOOL = 10
    TYPE_STR = 11
    TYPE_BYTES = 12
    TYPE_NONE = 13
    TYPE_COMPLEX = 14


cdef PyObject* NAME_LIST = PyUnicode_InternFromString("List")
cdef PyObject* NAME_TUPLE = PyUnicode_InternFromString("Tuple")
cdef PyObject* NAME_DICT = PyUnicode_InternFromString("Dict")
cdef PyObject* NAME_TYPED_DICT = PyUnicode_InternFromString("TypedDict")
cdef PyObject* NAME_SET = PyUnicode_InternFromString("Set")
cdef PyObject* NAME_LITERAL = PyUnicode_InternFromString("Literal")
cdef PyObject* NAME_ANY = PyUnicode_InternFromString("Any")
cdef PyObject* NAME_UNION = PyUnicode_InternFromString("Union")
cdef PyObject* NAME_ELLIPSIS = PyUnicode_InternFromString("Ellipsis")


cdef inline TypeID get_type_id(PyObject* name):

    if name == NAME_UNION: return TYPE_UNION
    if name == NAME_ANY: return TYPE_ANY
    if name == NAME_LIST: return TYPE_LIST
    return TYPE_UNKNOWN


cdef inline TypeID get_fast_type(PyObject* obj):
    if obj == <PyObject*>int: return TYPE_INT
    if obj == <PyObject*>str: return TYPE_STR
    return TYPE_COMPLEX


cdef inline int matches_origin(PyObject* obj, PyObject* type_obj):
    cdef PyObject * type_obj_name = NULL
    cdef PyObject * type_origin = NULL
    cdef TypeID type_id
    cdef const char* c_str

    type_obj_name = PyObject_GetAttr(type_obj, NAME_TXT)

    if type_obj_name != NULL:
        # PyUnicode_AsUTF8 returns the internal buffer; no .encode() needed!
        type_id = get_type_id(type_obj_name)
        # Clean up the reference immediately
        Py_XDECREF(type_obj_name)
        if type_id == TYPE_UNION or type_id == TYPE_ANY:
            return 1

    type_origin = PyObject_GetAttr(type_obj, ORIGIN_TXT)

    if type_origin != NULL:
        result = PyObject_TypeCheck(obj, Py_TYPE(type_origin))
        Py_XDECREF(type_origin)
        return result

    return 0

cdef inline int which_subtype(PyObject* element):
    cdef str element_name
    cdef PyObject* origin_type = NULL
    cdef PyObject* origin_name = NULL
    cdef PyObject* is_typed_dict = NULL
    cdef const char* c_str

    is_typed_dict = PyObject_GetAttr(element, IS_TYPEDDICT_TXT)
    if is_typed_dict != NULL:
        Py_XDECREF(is_typed_dict)
        return 30

    cdef object origins_tuple = get_origins(element)

    origin_type = PyTuple_GetItem(<PyObject*>origins_tuple, 0)

    if origin_type != NULL:
        # should happen when we have a real class not a Generic one
        Py_XDECREF(origin_type)
        return 0

    origin_name = PyTuple_GetItem(<PyObject*>origins_tuple, 1)
    if origin_name == NULL:
        return 0

    if origin_name == NAME_LIST:
        return 1
    if origin_name == NAME_TUPLE:
        return 2
    if origin_name == NAME_DICT:
        return 3
    if origin_name == NAME_LIST:
        return 4
    if origin_name == NAME_LITERAL:
        return 5
    if origin_name == NAME_ANY:
        return -2
    if origin_name == NAME_UNION:
        return -1
    if origin_name == NAME_ELLIPSIS:
        return 6

    return 0


cdef inline int sub_type_result(PyObject* obj, PyObject* type_obj, int subtype):
    cdef int result = 0

    if obj == NULL or type_obj == NULL:
        return result

    if subtype == -1:
        return union_element(obj, type_obj)
    if subtype == 1:
        return list_elements(<object>obj, <object>type_obj, object, object)
    if subtype == 2:
        return tuple_elements(<object>obj, <object>type_obj, object, object)
    if subtype == 3:
        return dict_elements(<object>obj, <object>type_obj, object, object)
    if subtype == 4:
        return set_elements(<object>obj, <object>type_obj, object, object)
    if subtype == 5:
        return literal_elements(<object>obj, <object>type_obj)
    if subtype == 30:
        return typeddict_element(<object>obj, <object>type_obj)

    return result

cdef tuple get_origins(PyObject* typ_to_check):

    """
    :param typ_to_check: typ_to_check: some typing like List[str], Dict[str, int], Tuple[Union[str, int], List[int]]
    :return: the class, alias_class and the class name
        - List[str] = (list, 'List')
        - Dict[str, int] = (dict, 'Dict')
        - Tuple[Union[str, int], List[int]] = (tuple, 'Tuple)
        - FunctionType = (None, 'None')
    """
    cdef PyObject* origin = NULL
    cdef PyObject* origin_name = NULL
    cdef PyObject* orig_base = NULL

    cdef PyObject* typ_annotations = PyObject_GetAttr(typ_to_check, ANNOTATIONS_TXT)
    cdef PyObject* typ_orig_bases = PyObject_GetAttr(typ_to_check, ORIG_BASES_TXT)
    cdef PyObject* type_origin = PyObject_GetAttr(typ_to_check, ORIGIN_TXT)
    cdef PyObject* type_origin_name = NULL

    py_tuple = PyTuple_New(2)

    if typ_annotations != NULL:
        if typ_orig_bases != NULL:
            list_item = PyList_GetItem(typ_orig_bases, 0)
            orig_base = PyObject_GetAttr(list_item, DUNDER_NAME_TXT)
        else:
            orig_base = PyObject_GetAttr(PyObject_GetAttr(PyObject_GetAttr(typ_to_check, CLASS_TXT), DUNDER_CLASS_TXT), DUNDER_NAME_TXT)

        Py_XDECREF(typ_annotations)
        Py_XDECREF(typ_orig_bases)
        Py_XDECREF(type_origin)

        PyTuple_SetItem(py_tuple, 0, <object> typ_to_check)
        PyTuple_SetItem(py_tuple, 1, <object> orig_base)
        PyErr_Clear()
        return py_tuple

    if type_origin != NULL:
        type_origin_name = PyObject_GetAttr(type_origin, DUNDER_NAME_TXT)
        if type_origin_name != NULL:
            origin = type_origin
            origin_name = type_origin_name
        elif typ_orig_bases != NULL:
            origin = typ_orig_bases
        else:
            origin = type_origin
    else:
        type_origin_name = PyObject_GetAttr(typ_to_check, NAME_TXT)
        if type_origin_name != NULL:
            origin_name = type_origin_name

    if type_origin_name == NULL:
        origin = PyObject_GetAttr(typ_to_check, DUNDER_CLASS_TXT)
        if origin != NULL:
            origin_name = PyObject_GetAttr(origin, DUNDER_NAME_TXT)

    Py_XDECREF(typ_annotations)
    Py_XDECREF(typ_orig_bases)
    Py_XDECREF(type_origin)

    PyTuple_SetItem(py_tuple, 0, <object>typ_to_check)
    PyTuple_SetItem(py_tuple, 1, <object>origin_name)
    PyErr_Clear()
    return py_tuple


cdef inline int union_element(PyObject* obj, PyObject* type_obj):
    cdef int result = 0
    cdef int pos = 0;
    cdef PyObject* type_args = PyObject_GetAttr(type_obj, ARGS_TXT)
    cdef PyObject* type_arg = NULL

    if type_args == NULL:
        return matches_origin(obj, type_obj)
    else:
        type_arg = PyTuple_GetItem(type_args, pos)
        while type_arg != NULL:
            result = matches_origin(obj, type_arg)
            if result > 0:
                return result
            pos += 1
            type_arg = PyTuple_GetItem(type_args, pos)
            Py_XDECREF(type_arg)
        Py_XDECREF(type_args)
    return result


cdef inline int element_check(PyObject* obj, PyObject* type_obj):
    cdef PyObject* type_args = PyObject_GetAttr(type_obj, ARGS_TXT)
    cdef PyObject* type_arg = NULL
    cdef int result = 0
    cdef int ttype
    cdef int pos = 0;

    type_arg = PyTuple_GetItem(type_args, pos)
    while type_arg != NULL:
        ttype = which_subtype(type_arg)

        if ttype == 0:
            if matches_origin(obj, type_arg) != 0:
                return 1
        elif ttype == -2:
            return -2
        elif ttype == not_supported:
            return not_supported
        else:
            if sub_type_result(<PyObject*>obj, <PyObject*>type_arg, ttype) != 0:
                return 1
    Py_XDECREF(type_arg)
    Py_XDECREF(type_obj)
    return result


cpdef int dict_elements(object obj_, object type_obj_, object args, object kwargs):
    cdef int obj_len = 0
    cdef int key_result = 0
    cdef int value_result = 0
    cdef Py_ssize_t pos = 0

    cdef PyObject* obj = <PyObject *> obj_
    cdef PyObject* type_obj = <PyObject *> type_obj_
    cdef PyObject* origin_name = NULL

    cdef PyObject* key_element = NULL
    cdef PyObject* value_element = NULL
    cdef PyObject* type_args = NULL
    cdef PyObject* key_type_args = NULL
    cdef PyObject* value_type_args = NULL
    cdef int type_key_type_args = 0
    cdef int type_value_type_args = 0

    type_args = PyObject_GetAttr(type_obj, ARGS_TXT) # returns a tuple

    if type_args == NULL:
        PyErr_Clear()
        return PyDict_Check(obj)
    else:
        tuple_size = PyTuple_Size(<object>type_args)

        if tuple_size == 0:
            PyErr_Clear()
            return 0
        if tuple_size < 2:
            if matches_origin(<PyObject *> obj, <PyObject *> type_obj) == 0:
                PyErr_Clear()
                return 0
            origins_tuple = get_origins(<PyObject*>type_obj)
            origin_name = PyTuple_GetItem(<PyObject *> origins_tuple, 1)
            if origin_name == NAME_DICT:
                return dict_elements(<object>obj, <object>PyTuple_GetItem(<PyObject *> origins_tuple, 0), object, object)
            if origin_name == NAME_TYPED_DICT:
                return typeddict_element(<object>obj, <object>type_obj)
            PyErr_Clear()
            return PyDict_Check(obj)

        key_type_args = PyTuple_GetItem(type_args, 0)
        value_type_args = PyTuple_GetItem(type_args, 1)

        type_key_type_args = which_subtype(key_type_args)
        type_value_type_args = which_subtype(value_type_args)

        while PyDict_Next(obj, &pos, &key_element, &value_element):
            if type_key_type_args != 0:
                key_result = sub_type_result(key_element, key_type_args, type_key_type_args)
            else:
                key_result = PyObject_TypeCheck(key_element, <PyTypeObject*>key_type_args)

            if type_value_type_args != 0:
                value_result = sub_type_result(value_element, value_type_args, type_value_type_args)
            else:
                value_result = PyObject_TypeCheck(value_element, <PyTypeObject*>value_type_args)

            if key_result <= 0:
                break
            if value_result <= 0:
                break

        PyErr_Clear()
        return 1


cpdef int set_elements(object obj, object type_obj, object args, object kwargs):
    cdef PyObject* type_args = PyObject_GetAttr(<PyObject*>type_obj, ARGS_TXT)
    cdef PyObject* set_element
    cdef int result = 0
    cdef int tmp = 0
    cdef int ttype
    cdef int pos = 0

    if type_args != NULL:

        if matches_origin(<PyObject*>obj, <PyObject*>type_obj) == 0:
            return 0

        set_element = PyTuple_GetItem(type_args, pos)
        while set_element != NULL:
            tmp = element_check(set_element, <PyObject*>type_obj)
            if tmp > 0:
                PyErr_Clear()
                return 1
            elif tmp == -2:
                PyErr_Clear()
                return 1
            elif tmp == not_supported:
                PyErr_Clear()
                return not_supported
            pos += 1
            set_element = PyTuple_GetItem(type_args, pos)
        PyErr_Clear()
        return result
    else:
        return matches_origin(<PyObject*>obj, <PyObject*>type_obj)


cdef inline bint ellipsis_inside(PyObject* type_obj):
    cdef PyObject* item = NULL
    cdef PyObject* iter_obj = PyObject_GetIter(type_obj)

    if iter_obj == NULL:
        return 0

    while True:
        item = PyIter_Next(iter_obj)
        if item == NULL:
            if PyErr_Occurred():
                return 0  # Actual error occurred
            break  # Normal end of iteration

        if which_subtype(item) == 6:
            # You MUST decref item here because PyIter_Next returns a NEW reference
            Py_XDECREF(item)
            return 1

        # You MUST decref item here because PyIter_Next returns a NEW reference
        Py_XDECREF(item)
        return 0

    # You MUST decref the iterator itself
    Py_XDECREF(iter_obj)

    return 0

cdef int validate_tuple_elements(object tuple_element, object type_arg):
    ttype = which_subtype(<PyObject*>type_arg)
    if ttype == 0:
        return isinstance(tuple_element, type_arg)
    elif ttype == -2:
        return 1
    elif ttype == not_supported:
        return not_supported
    else:
        return sub_type_result(<PyObject*>tuple_element, <PyObject*>type_arg, ttype)

cpdef int tuple_elements(object obj_, object type_obj, object args, object kwargs):
    cdef PyObject* type_args = PyObject_GetAttr(<PyObject*>type_obj, ARGS_TXT)
    cdef PyObject* obj = <PyObject *> obj_
    cdef object tuple_element
    cdef object type_arg
    cdef object origin_type
    cdef str origin_name
    cdef int result = 0
    cdef int ttype
    cdef int tmp
    cdef int num_params = 0

    return 1
    # if type_args != NULL:
    #
    #     if PyObject_TypeCheck(obj, Py_TYPE(type_obj)):
    #         if ellipsis_inside(type_args):
    #             for tuple_element in obj:
    #                 result += validate_tuple_elements(tuple_element, type_args[0])
    #             return result >= PyObject_Length(obj)
    #         elif PyObject_Length(obj) == PyObject_Length(type_args):
    #             for tuple_element, type_arg in zip(obj, type_args):
    #                 result += validate_tuple_elements(tuple_element, type_arg)
    #             return result >= PyObject_Length(obj)
    #         else:
    #             return 0
    #     else:
    #         return 0
    # else:
    #     if hasattr(type_obj, '_nparams'):
    #         num_params = type_obj._nparams
    #
    #     if num_params < 0:
    #         origin_type, origin_name = get_origins(<PyObject*>type_obj)
    #         return isinstance(obj, origin_type)
    #     for tuple_element, type_arg in zip(obj, type_obj):
    #         result += validate_tuple_elements(tuple_element, type_arg)
    #     return result >= len(obj)


cdef int c_list_elements(PyObject* obj, PyObject* type_obj):
    cdef PyObject* type_args = PyObject_GetAttr(type_obj, ARGS_TXT)
    cdef PyObject* list_element
    cdef int result = 0
    cdef int tmp = 0
    cdef int ttype
    cdef int pos = 0

    if type_args != NULL:

        if matches_origin(obj, type_obj) == 0:
            return 0

        list_element = PyTuple_GetItem(type_args, pos)
        while list_element != NULL:
            tmp = element_check(list_element, type_obj)
            if tmp > 0:
                PyErr_Clear()
                return 1
            elif tmp == -2:
                PyErr_Clear()
                return 1
            elif tmp == not_supported:
                PyErr_Clear()
                return not_supported
            pos += 1
            list_element = PyTuple_GetItem(type_args, pos)
        PyErr_Clear()
        return result
    else:
        return matches_origin(obj, type_obj)

cpdef int list_elements(object obj, object type_obj, object args, object kwargs):
    return c_list_elements(<PyObject*>obj, <PyObject*>type_obj)


cpdef int literal_elements(object obj, object type_obj):
    cdef PyObject* obj_ptr = <PyObject *> obj
    cdef PyObject* type_args = PyObject_GetAttr(<PyObject*>type_obj, ARGS_TXT)
    cdef int pos = 0
    cdef int result = 1
    cdef PyObject* literal_element = NULL

    if type_args != NULL:
        literal_element = PyTuple_GetItem(type_args, pos)
        while literal_element != NULL:
            if PyObject_RichCompareBool(obj_ptr, literal_element, result) == 1:
                return 0
        PyErr_Clear()
        return result
    else:
        return 0


cpdef int typeddict_element(object obj_, object type_obj_):
    """
    returns 0 as False, 1 as True
    """
    cdef PyObject* obj = <PyObject *> obj_
    cdef PyObject* type_obj = <PyObject *> type_obj_
    cdef int total = 1
    cdef int result = 0
    cdef int ttype = 0
    cdef int pos = 0
    cdef PyObject* required_fields = PyObject_GetAttr(type_obj, ANNOTATIONS_TXT)
    cdef PyObject* required_field_keys = NULL
    cdef PyObject* item = NULL

    if required_fields:
        required_field_keys = PyDict_Keys(required_fields)

    if required_field_keys == NULL:
        return 0

    item = PyList_GetItem(obj, pos)
    while item != NULL:
        ttype = which_subtype(PyDict_GetItem(required_fields, item))
        if ttype == 0:
            result = PyObject_TypeCheck(PyDict_GetItem(obj, item), Py_TYPE(PyDict_GetItem(required_fields, item)))
            if result == 0:
                return 0
        else:
            result = sub_type_result(PyDict_GetItem(obj, item), PyDict_GetItem(required_fields, item), ttype)
            if result == 0:
                return 0
        if result == -2:
            return -2

        pos += 1
        Py_XDECREF(item)
        item = PyList_GetItem(obj, pos)

    Py_XDECREF(required_field_keys)
    PyErr_Clear()
    return total
