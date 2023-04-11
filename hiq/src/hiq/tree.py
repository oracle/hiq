# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import os
import hiq
import itree
from hiq import tree_func
from hiq.constants import FORMAT_DATETIME, FORMAT_TIMESTAMP


itree.uuid()

# ZIN_THRESHOLD will overwrite the default value
global_zin_threshold = None


def init(
    sf,
    s="",
    tid="",
    extra=None,
    monotonic=True,
    capacity=1024,
    queue_lmk=None,
):
    """Constructor of Tree
    Args:
        s (str, optional): a string representation which a tree could be recovered from. Defaults to "".
        tid (str, optional): a unique id of the tree. Defaults to None.
        extra (dict, optional): extra information of the tree. Defaults to {}.
    """
    if not extra:
        extra = {}
    global global_zin_threshold
    if global_zin_threshold is None:
        global_zin_threshold = float(os.environ.get("ZIN_THRESHOLD", 1e-7))

    if not tid:
        # latency: 50us
        tid = itree.uuid()
    # interesting, the old syntax is required here :-)
    itree.Tree.__init__(
        sf,
        tid=tid,
        extra=extra,
        monotonic=monotonic,
        capacity=capacity,
        zin_threshold=global_zin_threshold,
    )

    if s:
        sf.recover(s)
    sf.queue_lmk = queue_lmk


def get_map():
    _map = {"__init__": init, "__slots__": ("queue_lmk",)}
    PREFIX = "tree_"
    for i in dir(tree_func):
        if i.startswith(PREFIX):
            itree.exe(f"_map[i[{len(PREFIX)}:]] = tree_func.{i}", locals())
    return _map


Tree = type(
    "Tree",
    (itree.Tree,),
    get_map(),
)


def get_graph_from_string(
    s: str,
    time_format=FORMAT_TIMESTAMP,
    whole_node_name="__predict",
    with_ordered_node=True,
) -> str:
    """deserialize a string back into a HiQ tree and return the graph representation and ordered duration to the caller


    >>> m = "t1^get_memory_mb,,0,54,5,0,1e-07,0#%n1*[None,inf,inf,0$0#[__predict,9942.6796875,10064.375,0$0#[__pdf,9942.6796875,10013.578125,0$0#][__txt,10013.578125,10175.28515625,0$0#[__det,10013.578125,10174.68359375,0$0#[__ort,10228.8984375,10357.7421875,0$0#]][__det,10174.68359375,10175.28515625,0$0#[__ort,10174.68359375,10175.28515625,0$0#]]][_ort_sess,10175.28515625,10255.44921875,0$0#]]]"
    >>> print(get_graph_from_string(m))
    [      9942.680 -      10064.375]  [100.00%] 🟢_root_get_memory_mb(121.6953)
    [      9942.680 -      10064.375]  [100.00%]    l___predict(121.6953)
    [      9942.680 -      10013.578]  [ 58.26%]       |___pdf(70.8984)
    [     10013.578 -      10175.285]  [132.88%]       |___txt(161.7070)
    [     10013.578 -      10174.684]  [132.38%]       |  |___det(161.1055)
    [     10228.898 -      10357.742]  [105.87%]       |  |  l___ort(128.8438)
    [     10174.684 -      10175.285]  [  0.49%]       |  l___det(0.6016)
    [     10174.684 -      10175.285]  [  0.49%]       |     l___ort(0.6016)
    [     10175.285 -      10255.449]  [ 65.87%]       l__ort_sess(80.1641)
    ordered lowest level calls:__ort:129.4453, _ort_sess:80.1641, __pdf:70.8984

    """
    t = Tree(s)
    entire_latency = t.get_duration_by_node_name(whole_node_name)
    tracking_overhead = float("-inf")  # t.get_overhead()
    if "overhead" in t.extra:
        tracking_overhead = float(t.extra["overhead"]) / (entire_latency * 1e4)
    graph = t.get_graph(time_format)
    res = graph
    if with_ordered_node:
        ordered_duration = t.leaf_duration_by_name_s(ordered=3)
        res += f"ordered lowest level calls:{ordered_duration}\n"
    if "overhead" in t.extra:
        res += f"{tracking_overhead=:.3f}%"
    return res


def get_duration_from_hiq_string(s: str, key: str) -> float:
    """
    >>> m = "t1^get_memory_mb,,0,54,5,0,1e-07,0#%n1*[None,inf,inf,0$0#[__predict,9942.6796875,10064.375,0$0#[__pdf,9942.6796875,10013.578125,0$0#][__txt,10013.578125,10175.28515625,0$0#[__det,10013.578125,10174.68359375,0$0#[__ort,10228.8984375,10357.7421875,0$0#]][__det,10174.68359375,10175.28515625,0$0#[__ort,10174.68359375,10175.28515625,0$0#]]][_ort_sess,10175.28515625,10255.44921875,0$0#]]]"
    >>> print(get_duration_from_hiq_string(m, "__txt"))
    161.70703125
    >>> print(get_duration_from_hiq_string(m, "__ort"))
    129.4453125
    """
    t = Tree(s)
    node_names = t.get_distinct_node_names()
    if key not in node_names:
        raise ValueError(
            f"😬 could not find {key} in hiq tree. hiq_str: {s}, valid nodes: {node_names}"
        )
    return t.get_duration_by_node_name(key)


if __name__ == "__main__":
    m = "t1^get_memory_mb,,0,54,5,0,1e-07,0#%n1*[None,inf,inf,0$0#[__predict,9942.6796875,10064.375,0$0#[__pdf,9942.6796875,10013.578125,0$0#][__txt,10013.578125,10175.28515625,0$0#[__det,10013.578125,10174.68359375,0$0#[__ort,10228.8984375,10357.7421875,0$0#]][__det,10174.68359375,10175.28515625,0$0#[__ort,10174.68359375,10175.28515625,0$0#]]][_ort_sess,10175.28515625,10255.44921875,0$0#]]]"
    print(get_graph_from_string(m, with_ordered_node=False))

    print(
        get_graph_from_string(m, time_format=FORMAT_DATETIME, whole_node_name="__txt")
    )

    print(get_duration_from_hiq_string(m, "__ort"))

    import pickle

    a = Tree("", "tid_123", {})

    print(a)
    print(dir(a))
    r = a.get_root()
    print(r)

    d = pickle.dumps(a)
    print(d)
    h2 = pickle.loads(d)
    d2 = pickle.dumps(h2)
    # print(d2)
    print(d == d2)
