# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import json
import os
import re

from collections.abc import Mapping
from collections import UserDict
from collections import namedtuple


CLS_NAME = "GAMMA_DYNAMIC_DICT"
PREFIX = "o_"

__all__ = ["ddlist", "ddjson", "ddyaml"]


def ddlist(keys=[], values=[], name=CLS_NAME):
    mapping = dict(zip(keys, values))
    return _mapper(mapping, _nt_name=name)


def ddjson(data_or_path: str, name=CLS_NAME):
    if os.path.exists(data_or_path):
        with open(data_or_path, "r", encoding="UTF-8") as f:
            return _mapper(json.load(f), _nt_name=name)
    return _mapper(json.loads(data_or_path), _nt_name=name)


def ddyaml(data_or_path: str, name=CLS_NAME):
    if not os.path.exists(data_or_path):
        return _mapper(data_or_path, _nt_name=name)
    import yaml

    with open(data_or_path, "r", encoding="UTF-8") as file:
        data = yaml.load(file, yaml.FullLoader)
        return _mapper(data, _nt_name=name)


def _mapper(mapping, _nt_name=CLS_NAME):
    """Convert mappings to namedtuple recursively."""
    if isinstance(mapping, Mapping) and not isinstance(mapping, AsDict):
        for key, value in list(mapping.items()):
            mapping[key] = _mapper(value)
        return namedtuple_wrapper(_nt_name, **mapping)
    elif isinstance(mapping, list):
        return [_mapper(item) for item in mapping]
    return mapping


def namedtuple_wrapper(_nt_name, **kwargs):
    import keyword

    n = {}
    for k, v in kwargs.items():
        nk = re.sub(r"[^0-9a-zA-Z_]+", "_", k)
        n[PREFIX + nk] = v
    wrap = namedtuple(_nt_name, n)
    return wrap(**n)


class AsDict(UserDict):
    """placeholder"""


def ignore(mapping):
    if isinstance(mapping, Mapping):
        return AsDict(mapping)
    elif isinstance(mapping, list):
        return [ignore(item) for item in mapping]
    return mapping


def is_namedtuple_instance(x):
    _type = type(x)
    bases = _type.__bases__
    if len(bases) != 1 or bases[0] != tuple:
        return False
    fields = getattr(_type, "_fields", None)
    if not isinstance(fields, tuple):
        return False
    return all(type(i) == str for i in fields)


def _reducer(obj):
    if isinstance(obj, dict):
        return {key: _reducer(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_reducer(value) for value in obj]
    elif is_namedtuple_instance(obj):
        return {key: _reducer(value) for key, value in obj._asdict().items()}
    elif isinstance(obj, tuple):
        return tuple(_reducer(value) for value in obj)
    else:
        return obj
