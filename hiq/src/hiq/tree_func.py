# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import ast
import io
import operator
import os

import sys
import traceback
from collections import defaultdict
from typing import List

import itree
from hiq.constants import FORMAT_TIMESTAMP
from hiq.node_utils import _c, _d
from hiq.tree_utils import split_extra
from hiq.node_utils import __peek_tree, _pp_tree
from hiq.utils import get_env_bool


def get_dict(**kwargs):
    return kwargs


def tree_start(sf, a, b, extra=None):
    if extra is None:
        extra = {}
    sf.discover(a, b, extra)
    if sf.queue_lmk:
        sf.queue_lmk.put_nowait(
            get_dict(id_=sf.tid, name=a, value=b, extra=extra, is_start=True)
        )


def tree_end(sf, a, b, extra=None):
    if extra is None:
        extra = {}
    try:
        sf.finish(a, b, extra)
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
    if sf.queue_lmk:
        sf.queue_lmk.put_nowait(
            get_dict(id_=sf.tid, name=a, value=b, extra=extra, is_start=False)
        )


def tree_consolidate(sf):
    if len(sf.stk) > 1:
        # print("no need to consolidate an incomplete tree")
        return
    sf.root = itree._itree.consolidate(sf.root)


def tree_recover(sf, s):
    if s:
        sf.deserialize(s)


def tree_repr(sf) -> str:
    return itree._itree.serialize_tree_(sf)


def tree_total_duration_s(sf):
    if sf.monotonic:
        return sf.root.span()
    else:
        raise NotImplementedError("TODO")


def tree_duration_by_name_s(sf) -> dict:
    if not sf.root:
        return {}
    visited = [sf.root]
    stack = [sf.root]
    res = defaultdict(float)
    res[sf.root.name] = sf.root.span()
    while stack:
        nd = stack[-1]
        if nd not in visited:
            visited.append(nd)
        remove_from_stack = True
        for nex in nd.nodes:
            if nex not in visited:
                stack.append(nex)
                res[nex.name] += nex.span()
                remove_from_stack = False
                break
        if remove_from_stack:
            stack.pop()
    return dict(res)


def tree_leaf_duration_by_name_s(sf, ordered=0):
    if not sf.root:
        return {}
    visited = [sf.root]
    stack = [sf.root]
    res = defaultdict(float)
    if not sf.root.nodes:
        res[sf.root.name] = sf.root.span()
    while stack:
        nd = stack[-1]
        if nd not in visited:
            visited.append(nd)
        remove_from_stack = True
        for nex in nd.nodes:
            if nex not in visited:
                stack.append(nex)
                remove_from_stack = False
                break
        if remove_from_stack and stack:
            if stack[-1] and not stack[-1].nodes:  # leaf node
                res[stack[-1].name] += stack[-1].span()
            stack.pop()
    res = dict(res)
    if ordered == 1:
        return dict(sorted(res.items(), key=operator.itemgetter(1), reverse=True))
    elif ordered == 2:
        return dict(sorted(res.items(), key=operator.itemgetter(1), reverse=False))
    elif ordered == 3:
        dt = dict(sorted(res.items(), key=operator.itemgetter(1), reverse=True))
        sio = io.StringIO()
        for key, value in dt.items():
            print(f"{key}:{value:6.4f}, ", end="", file=sio)
        return sio.getvalue().strip(", ")
    return dict(res)


def tree_leaf_duration_total_s(sf) -> float:
    res = sf.leaf_duration_by_name_s()
    total = sum(res.values())
    return total


def tree_get_distinct_node_names(sf) -> List[str]:
    r = set()

    def __d(n):
        if not n:
            return
        nonlocal r
        r.add(n.name)
        for i in n.nodes:
            __d(i)

    __d(sf.root)
    r.discard(None)
    return list(r)


def tree_get_duration_by_node_name(s, name) -> float:
    r = 0.0

    def __d(n):
        if not n:
            return
        nonlocal r
        if n.name == name:
            r += n.span()
        [__d(i) for i in n.nodes]

    __d(s.root)
    return r


def tree_get_duration_by_node_name_and_level(s, name, level) -> float:
    """root(None node) is level 0"""
    r = 0.0
    q, level_ = [s.root], 0
    while len(q) > 0:
        tmp = []
        for i in q:
            for j in i.nodes:
                tmp.append(j)
                if level_ == level:
                    if j.name == name:
                        r += j.span()
        level_ += 1
        q = tmp
    return r


def tree_show(s, time_format=FORMAT_TIMESTAMP):
    print(s.get_graph(time_format))


def tree_get_graph(sf, time_format=FORMAT_TIMESTAMP) -> str:
    sf.consolidate()
    sio = io.StringIO()
    wide_output, value_column_len, _type = __peek_tree(sf.root)
    wide_output = get_env_bool("WIDE_OUTPUT", wide_output)
    _pp_tree(
        sf.root,
        time_format=time_format,
        file=sio,
        root_name=sf.tid,
        wide_output=wide_output,
        value_column_len=value_column_len,
        _type=_type,
        tree_extra=sf.extra,
    )
    return sio.getvalue()


def tree_just_before_ending_root(s):
    return len(s.stk) <= 2


# It is pickale, and serializable!!!
# In addition to pickling, for multiprocess code, we can pass the `repr()` between processes.
# There lmk_queue will be lost after pickling :-)
def tree___getstate__(self):
    a_state = itree.Tree.__getstate__(self)
    b_state = self.__dict__
    return (a_state, b_state)


def tree___setstate__(self, state):
    a_state, b_state = state
    self.__dict__ = b_state
    self.queue_lmk = None
    itree.Tree.__setstate__(self, a_state)
