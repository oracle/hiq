# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import ast
import base64

import itree
from hiq.node import Node
from hiq.constants import *
from hiq.utils import ts_pair_to_dt, memoize
from typing import Union


def __create_tmp_node():
    return Node("", 0, 0)


def _d(n: Node, s: str = ""):
    """serialize a tree(the node and its children) to string
    Since A node is well-defined, we can use format like `{name,start,end,duration}` to serialize it.
    """
    if n:
        extra_ = ""
        if n.extra:
            extra_ = dict_to_b64_str(n.extra)
        s += '{"' + str(n.name) + '":' + str(n.start) + "," + str(n.end) + "," + extra_
        for i in n.nodes:
            s = _d(i, s)
        s += "}"
    return s


def is_str_dict(s):
    try:
        r = ast.literal_eval(s)
        if isinstance(r, dict):
            return True
    except:
        return False


def str_to_number(x) -> Union[int, float]:
    x = float(x)
    if x.is_integer():
        return int(x)
    else:
        return x


def __parse_node(s):
    _start, _end, _extra = s.split(",")

    if _extra and _extra != "inf":
        _extra = b64_str_to_dict(_extra)
    # _extra should be a dictionary
    if _extra and isinstance(_extra, str) and not is_str_dict(_extra):
        _extra = {}
    _sta = str_to_number(_start)
    _end = str_to_number(_end)
    if _extra == "":
        _extra = {}
    return _sta, _end, _extra


def _c(bs: str) -> Node:
    """de-serialize a string to a node"""
    if not bs:
        return None
    stk_ = [itree.create_virtual_node()]
    s = ""
    for ch in bs:
        if ch == "{":
            if len(stk_) == 1:
                stk_.append(__create_tmp_node())
                stk_[0].append(stk_[1])
            else:
                if s:
                    kv = s.split(":")
                    stk_[-1].name = kv[0][1:-1]
                    stk_[-1].start, stk_[-1].end, stk_[-1].extra = __parse_node(kv[1])
                    s = ""

                t = __create_tmp_node()
                stk_[-1].append(t)
                stk_.append(t)
        elif ch == "}":
            if s:
                kv = s.split(":")
                stk_[-1].name = kv[0][1:-1]
                stk_[-1].start, stk_[-1].end, stk_[-1].extra = __parse_node(kv[1])
                s = ""
            if len(stk_) > 1:
                stk_.pop()
        else:
            s += ch
    assert len(stk_) == 1, "bad tree data"
    n = itree._itree.consolidate(stk_[0])
    return n


def __peek_tree(node, debug=False):
    """look 2 levels deep to find the meta information of the tree

    Args:
        node (Node): root node of a tree
    Returns:
        wide_output, value_column_len
    """
    wide_output = False
    if node.extra and "start" in node.extra or "end" in node.extra:
        wide_output = True
    if not wide_output and len(node.nodes) > 0:
        if "start" in node.nodes[0].extra or "end" in node.nodes[0].extra:
            wide_output = True
    value_lens = []
    values = []

    _type = None

    def __d(n):
        nonlocal value_lens, _type, values, debug
        value_lens.append(len(str(n.start)))
        value_lens.append(len(str(n.end)))
        if debug:
            values.append(str(n.start))
            values.append(str(n.end))
        if _type is None or _type == "int":
            if isinstance(n.start, int):
                _type = "int"
            else:
                _type = "float"
        for x in n.nodes:
            __d(x)

    __d(node)
    value_column_len = max(value_lens)
    return wide_output, value_column_len, _type


DEFAULT_FLOAT_DIGIT = 3
TREE_COL_DIS = 1


def _pp_tree(
    node,
    time_format=FORMAT_TIMESTAMP,
    file=None,
    _prefix="",
    _last=True,
    span=None,
    level=1,
    root_name=TREE_ROOT_NAME,
    wide_output=False,
    value_column_len=14,
    _type="float",
    _float_digit=DEFAULT_FLOAT_DIGIT,
    tree_extra=None,
):
    """pretty print in tree format"""
    if not tree_extra:
        tree_extra = {}
    _p = ""
    if wide_output:
        if node.extra:
            if time_format == FORMAT_TIMESTAMP:
                if _type == "float":
                    number_format = f"%{11+_float_digit}.{_float_digit}f"
                    _p += (
                        f"[{number_format%node.extra[EXTRA_START_TIME_KEY]} - {number_format%node.extra[EXTRA_END_TIME_KEY]}]"
                        + " " * 2
                    )
                else:
                    number_format = r"%14.0f"
                    _p += (
                        f"[{number_format%node.extra[EXTRA_START_TIME_KEY]} - {number_format%node.extra[EXTRA_END_TIME_KEY]}]"
                        + " " * 2
                    )
            elif time_format == FORMAT_DATETIME:
                _p += (
                    f"[{ts_pair_to_dt(node.extra[EXTRA_START_TIME_KEY], node.extra[EXTRA_END_TIME_KEY])}]"
                    + " " * 2
                )
            else:
                raise ValueError(f"wrong time format: {time_format}")
        else:
            if time_format == FORMAT_DATETIME:
                _p += " " * (42 + _float_digit * 2)
                # _p += f"[{number_format%0} - {number_format%0}]" + " " * 2
            else:
                _p += " " * (29 + _float_digit * 2)
    if isinstance(node.start, str):
        raise ValueError(f"wrong type of node.start: {node.start}")
    if len(str(node.start)) >= TS_LEN and float(node.start) > 1633299120 // 2:
        if time_format == FORMAT_TIMESTAMP:
            number_format = f"%{value_column_len-_float_digit}.{_float_digit}f"
            # _p += f"[{node.start:14.3f} ~ {node.end:14.3f}]" + " " * 2
            _p += (
                f"[{number_format%node.start} - {number_format%node.end}]"
                + " " * TREE_COL_DIS
            )
        elif time_format == FORMAT_DATETIME:
            _p += f"[{ts_pair_to_dt(node.start, node.end)}]" + " " * TREE_COL_DIS
        else:
            raise ValueError(f"wrong time format: {time_format}")
    else:
        # number_len = max(len(str(node.start)), len(str(node.end)))
        if _type == "float":
            # number_format = f"%{value_column_len+_float_digit}.{_float_digit}f"
            number_format = f"%{value_column_len}.{_float_digit}f"
            # print(number_format)
            _p += (
                f"[{number_format%node.start} - {number_format%node.end}]"
                + " " * TREE_COL_DIS
            )
        else:
            number_format = f"%{value_column_len}.0f"
            _p += (
                f"[{number_format%node.start} - {number_format%node.end}]"
                + " " * TREE_COL_DIS
            )
    if span is None:
        span = node.span() if level > 0 else 0
        branch = "🟢"
    else:
        branch = "l"
    if span != 0:
        _p += f" [{(node.span())*100/span:6.2f}%]" + " " * TREE_COL_DIS
    else:
        _p += " [000.00%]" + " " * TREE_COL_DIS
    _node_name = (
        f"root_{root_name}" if (is_none(node.name) and level == 1) else node.name
    )
    if node.extra:
        if wide_output:
            del node.extra[EXTRA_START_TIME_KEY], node.extra[EXTRA_END_TIME_KEY]
        contents = f"{_node_name}({node.span():6.4f})"  # TODO: no time to do it
        if node.extra:
            contents += f" ({str(node.extra)})"
    else:
        contents = f"{_node_name}({node.span():6.4f})"
    if level == 1 and tree_extra:
        # print("🤑" * 40, id(tree_extra))
        overhead_str, tree_extra_str = "", ""
        if "overhead" in tree_extra:
            overhead_str = f"[OH:{int(tree_extra['overhead'])}us]"
            del tree_extra["overhead"]
            del tree_extra["overhead_start"]
        if len(tree_extra) > 0:
            pretty_ = concise_dict(tree_extra)
            if pretty_:
                tree_extra_str = f"[{pretty_}]"
        prefix_length = len(_p + _prefix) + 2
        if tree_extra_str:
            contents += "\n" + " " * prefix_length + tree_extra_str
        if overhead_str:
            contents += "\n" + " " * prefix_length + overhead_str
    print(_p, _prefix, branch + "_" if _last else "|_", contents, sep="", file=file)
    _prefix += "   " if _last else "|  "
    child_count = len(node.nodes)
    for i, child in enumerate(node.nodes):
        _last = i == (child_count - 1)
        _pp_tree(
            child,
            time_format,
            file,
            _prefix,
            _last,
            span=span,
            level=level + 1,
            wide_output=wide_output,
            value_column_len=value_column_len,
            _type=_type,
        )


def concise_dict(d: dict):
    _d = {}
    for k, v in d.items():
        if isinstance(v, str) and len(v) > 20:
            _d[k] = "..." + v[-20:]
        elif not v:
            pass
        else:
            _d[k] = v
    return _d


def is_none(x) -> bool:
    return x is None or x.lower() == "none"


def dict_to_b64_str(d: dict):
    """d is a dictionary with strings/int/float inside"""
    b64 = base64.b64encode(bytes(str(d), "utf-8"))
    return b64.decode("utf-8")


@memoize
def b64_str_to_dict(s: str) -> dict:
    """d is a dictionary with strings/int/float inside"""
    try:
        d = base64.b64decode(s).decode("utf-8")
        r = ast.literal_eval(d)
        return r
    except Exception as e:
        return {}
