# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

__author__ = None

import collections
import gc
import inspect
import io
import os
import re
import sys
import time
import traceback
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import *

import hiq
import itree
from hiq.constants import *
from hiq.hiq_utils import (
    _is_callable,
    call_decorated,
    func_args_handler,
    get_global_hiq_status,
    get_hiq_table,
    get_tau_id,
    HiQIdGenerator,
)
from hiq.jack import Jack
from hiq.monkeyking import LogMonkeyKing
from hiq.tree import Tree
from hiq.utils import _check_overhead, _get_full_argspecs, is_hiqed
from hiq.memory import get_memory_mb, total_gpu_memory_mb

here = os.path.dirname(os.path.realpath(__file__))

# lib, class, func, tag
import inspect
import types


def parse_lib(lib_name, res=[]):
    if len(res) > 100:
        return res
    md = hiq.mod(lib_name)
    if md is None:
        return None
    p = [lib_name, "", "", ""]
    l = [i for i in dir(md) if not i.startswith("_") or i == "__call__"]
    for i in l:
        try:
            st = f"__m=type(md.{i})"
            itree.exe(st, locals())
            if (
                locals()["__m"] == types.FunctionType
                or locals()["__m"] == types.MethodType
            ):
                itree.exe(f"__m_len =len(inspect.getsourcelines(md.{i})[0])", locals())
                if locals()["__m_len"] < 10:
                    continue
                p[2], p[3] = i, i
                res.append(list(p))
                if len(res) > 100:
                    return res
            elif locals()["__m"] == type:
                p[1] = i
                itree.exe(f"__dir_list=dir(md.{i})", locals())
                fs = [
                    i
                    for i in locals()["__dir_list"]
                    if not i.startswith("_") or i == "__call__"
                ]
                for j in fs:
                    st = f"__m2=type(md.{i}.{j})"
                    itree.exe(st, locals())
                    if locals()["__m2"] == types.FunctionType:
                        itree.exe(
                            f"__m_len =len(inspect.getsourcelines(md.{i}.{j})[0])",
                            locals(),
                        )
                        if locals()["__m_len"] < 10:
                            continue
                        p[2], p[3] = j, j
                        res.append(list(p))
                p[1] = ""
            elif locals()["__m"] == types.ModuleType or "<class 'abc.ABCMeta'>" == str(
                locals()["__m"]
            ):
                r = parse_lib(f"{lib_name}.{i}", res)
                if r is not None:
                    res += r
                    if len(res) > 100:
                        return res[:100]
                print(st, ", mtype:", locals()["__m"])

        except AttributeError:
            continue
    return res


class HiQException(Exception):
    pass


class HiQBase(itree.ForestStats, LogMonkeyKing):
    __metaclass__ = ABC
    __no_none_key__ = False
    __slots__ = ()

    def __init__(
        sf,
        hiq_table_or_path: Union[str, List[Iterable[str]]] = [],
        metric_funcs: List[Callable] = [time.time],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table: List[str] = [],
        attach_timestamp=False,
        extra_metrics: Set[ExtraMetrics] = set(),  # EXTRA_METRIC_FILE
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
        *args,
        **kwargs,
    ):
        """constructor of ABC HiQBase

        Args:
            hiq_table_or_path (Union[str, List[Iterable[str]]], optional): this is an HiQ Conf, please refer to *HiQ Core Concepts* section in the HiQ documentation.Defaults to [].
            metric_funcs (List[Callable], optional): simple metric function with empty argument. Defaults to [time.time].
            hiq_id_func (Callable, optional): a callable to generate unique id for tau, the hiq map. Defaults to hiq.hiq_utils.get_tau_id.
            func_args_handler(Callable, optional): a callable to convert function args/kwargs into a string. Defaults to hiq.hiq_utils.func_args_handler.
            target_path (str, optional): the directory of the target code. Defaults to None.
            max_hiq_size (int, optional): the max size of hiq map. if the number is exceeded, tree will be sent to LMK. Defaults to 30.
            verbose (bool, optional): when verbose is true, more information will be recorded, like the full stack trace of exception will be recorded in HiQ tree node. Defaults to False.
            fast_fail (bool, optional): when it is true, raise exception to the upper level, don't swallow exceptions. Defaults to True.
            tpl (str, optional): hiq tpl path. Defaults to None.
            extra_hiq_table (List[str], optional): a list of string to decide to include metrics other than latency. Defaults to [].
            attach_timestamp (bool, optional): for non-time/non-latency metric tree, should we attach start, end timestamps in the extra dictionary? Defaults to False.
            extra_metrics (set, optional): metrics to track in `extra` field of HiQ node. The value could be EXTRA_METRIC_ARGS, EXTRA_METRIC_FILE or EXTRA_METRIC_FUNC and it is normally used in development environment. Defaults to set().
        """
        super().__init__()
        LogMonkeyKing.__init__(sf, lmk_path, lmk_handler, lmk_logger)
        if verbose:
            print("process 🆔 {}".format(os.getpid()))
        if target_path and target_path not in sys.path:
            sys.path.append(target_path)
        sf.tau = collections.defaultdict(dict)
        sf.count = 0
        sf.max_hiq_size = max_hiq_size
        hiq_quadruple = get_hiq_table(hiq_table_or_path)
        # for t in extra_hiq_table:
        #    hiq_quadruple.append(t)
        hiq_quadruple += extra_hiq_table
        sf._verify_input(hiq_quadruple)
        sf.get_tau_id = hiq_id_func
        sf.get_func_args = func_args_handler
        sf.verbose = verbose
        sf.fast_fail = fast_fail
        sf.attach_timestamp = attach_timestamp
        sf.extra_metrics = extra_metrics
        sf.__load_hiq_tpl(tpl)
        sf.metric_funcs = metric_funcs
        sf.__load_extra_metrics(extra_hiq_table)
        sf.enable_hiq()
        sf.check_oh_counter = 0

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.disable_hiq()

    def __load_hiq_tpl(sf, tpl):
        if tpl and os.path.exists(tpl):
            sf.load_tpl(tpl)
            return
        tpl = f"{here}/{TAU_TPL_LOC}"
        if os.path.exists(tpl):
            sf.load_tpl(tpl)
            return
        tpl = f"{here}/{TAU_PKL_LOC}"
        if os.path.exists(tpl):
            sf.itree_tpl = hiq.mod("pickle").load(open(tpl, "rb"))
        if not sf.itree_tpl:
            raise Exception(f"🈚️ empty tau tpl. tpl:{tpl}")

    def __load_extra_metrics(sf, extra_hiq_table):
        if TAU_TABLE_DIO_RD in extra_hiq_table:
            sf.metric_funcs.append(sf.get_dio_bytes_r)
        if TAU_TABLE_DIO_WT in extra_hiq_table:
            sf.metric_funcs.append(sf.get_dio_bytes_w)
        if HIQ_TABLE_SIO_RD in extra_hiq_table:
            sf.metric_funcs.append(sf.get_sio_bytes_r)
        if HIQ_TABLE_SIO_WT in extra_hiq_table:
            sf.metric_funcs.append(sf.get_sio_bytes_w)
        if TAU_TABLE_NIO_GET in extra_hiq_table:
            sf.metric_funcs.append(sf.get_nio_bytes_r)
        if TAU_TABLE_NIO_POS in extra_hiq_table:
            sf.metric_funcs.append(sf.get_nio_bytes_w)

    def _verify_input(sf, hiq_quadruple):
        sf.hiq_quadruple = []
        tag_names = set()
        for i in hiq_quadruple:
            i = list(i)
            if len(i) > 0 and i[0].startswith("#"):
                continue
            if len(i) != 4 or not isinstance(i[3], str) or len(i[3]) < 1:
                raise ValueError("🦉 tau table must have exact 4 columns")
            i[3] = (
                (HIQ_FUNC_PREFIX + i[3])
                if len(i[3]) >= 2 and i[3][:2] != HIQ_FUNC_PREFIX
                else i[3]
            )
            if i[3] in tag_names:
                raise ValueError(f"🦉 duplicated tag: {i[3]} in tau input!")
            if not re.match(r"^\w+$", i[3]):
                raise ValueError(
                    "🦉 only alpha numerics are allowed in tag but got: {i[3]}!"
                )
            tag_names.add(i[3])
            sf.hiq_quadruple.append(i)

    def set_extra_metrics(sf, extra_metrics: Iterable[ExtraMetrics]):
        """set extra metric information so that these information will enter the span node"""
        sf.extra_metrics = extra_metrics

    def get_tree(s, func: Callable, extra=None) -> Tree:
        """find the hiq tree, and attach extra on the tree if necessary
        Note: the extra information here will enter into tree level. To pass extra into node level, use `Tree.start()`.
        """
        if not extra:
            extra = {}
        if s.get_tau_id is None:
            s.get_tau_id = HiQIdGenerator()
        req_id = s.get_tau_id()
        if not req_id and HiQBase.__no_none_key__:
            print(f"warning: tau id is {req_id}")
        fn = func.__name__
        if req_id not in s.tau or fn not in s.tau[req_id]:
            if fn in [KEY_LATENCY]:
                s.tau[req_id][fn] = Tree(
                    extra=extra,
                    tid=fn,
                    queue_lmk=s.queue_lmk,
                )
            else:
                s.tau[req_id][fn] = Tree(
                    extra=extra,
                    tid=fn,
                    monotonic=False,
                    queue_lmk=s.queue_lmk,
                )
        if extra:
            s.tau[req_id][fn].extra.update(extra)
        r = s.tau[req_id][fn]
        if len(s.tau) > s.max_hiq_size + 1:
            d = s.tau.pop(list(s.tau.keys())[0])
            if hasattr(s, "send_trees_to_jack"):
                s.send_trees_to_jack(d)
        return r

    @_check_overhead
    def pre_processing(s, f_name, args=(), kwargs=None, tree_extra=None):
        """collect extra information for node"""
        if not kwargs:
            kwargs = {}
        if not tree_extra:
            tree_extra = {}
        log_monkey_file = os.environ.get("LOG_MONKEY_FILE", False)
        node_extra = {}
        if ExtraMetrics.ARGS in s.extra_metrics:
            if args:
                node_extra["args"] = s.get_func_args(args, f_name)
            if kwargs:
                node_extra["kwargs"] = s.get_func_args(kwargs, f_name)
        if ExtraMetrics.FILE in s.extra_metrics or log_monkey_file:
            caller = inspect.stack()[3]
            node_extra["file"] = f"{caller.filename}:{caller.lineno}"
        if ExtraMetrics.FUNC in s.extra_metrics:
            caller = inspect.stack()[3]
            node_extra["function"] = caller.function
        for func in s.metric_funcs:
            tmp = s.get_tree(func, extra=tree_extra)
            if func.__name__ == KEY_LATENCY:
                if "overhead_start" not in tmp.extra:
                    tmp.extra["overhead_start"] = s.overhead_us
                if EXTRA_START_TIME_KEY in node_extra:
                    del node_extra[EXTRA_START_TIME_KEY]
            else:
                if s.attach_timestamp:
                    node_extra[EXTRA_START_TIME_KEY] = time.time()
            an_extra = deepcopy(node_extra) if node_extra else {}
            # if s.overhead_us == 0:
            #    print(f"🤠,{func=},{id(tmp)=},{id(an_extra)=}")
            tmp.start(f_name, func(), extra=an_extra)

    @_check_overhead
    def post_processing(s, f_name):
        extra = {}
        for func in s.metric_funcs:
            if func.__name__ == KEY_LATENCY:
                if EXTRA_END_TIME_KEY in extra:
                    del extra[EXTRA_END_TIME_KEY]
            else:
                if s.attach_timestamp:
                    extra[EXTRA_END_TIME_KEY] = time.time()
            s.get_tree(func).end(f_name, func(), extra=deepcopy(extra) if extra else {})
        #########################################################

    @_check_overhead
    def update_overhead(s):
        # check tracing overhead
        for func in s.metric_funcs:
            if func.__name__ == KEY_LATENCY:
                tmp = s.get_tree(func)
                if tmp.just_before_ending_root():
                    tmp.extra["overhead"] = s.overhead_us - tmp.extra["overhead_start"]
                    # print(
                    #    f"👿, {func=},{id(tmp)=},{id(tmp.extra)=},"
                    #    f"{tmp.extra['overhead_start']=},{tmp.extra['overhead']=}"
                    # )

    @_check_overhead
    def handle_exception(s, f_name, e):
        """handle exception from calling the original function

        `fast_fail` means raising exception to the upper level, don't swallow exceptions

        Args:
            f_name (string): original function name
            e (Exception): the exception raised from the original function

        Raises:
            e: the original exception
        """
        node_extra = {KEY_EXC_SUM: e}
        if s.verbose:
            sio = io.StringIO()
            traceback.print_exc(file=sio)
            trace_msg = sio.getvalue()
            node_extra[KEY_EXC_TRA] = trace_msg
        if s.fast_fail:
            for func in s.metric_funcs:
                if func.__name__ == KEY_LATENCY:
                    if EXTRA_END_TIME_KEY in node_extra:
                        del node_extra[EXTRA_END_TIME_KEY]
                else:
                    if s.attach_timestamp:
                        node_extra[EXTRA_END_TIME_KEY] = time.time()
                tmp = s.get_tree(func)  # TODO: we can add exception here
                if func.__name__ == KEY_LATENCY and tmp.just_before_ending_root():
                    tmp.extra["overhead"] = (
                        s.overhead_us - tmp.extra["overhead_start"]
                    ) / len(s.metric_funcs)
                tmp.end(f_name, func(), extra=deepcopy(node_extra))
            raise e

    def inserter(s, f, *_args, **_kwargs):
        """If function signature has no positional argument, we can use this inserter directly."""

        def __x(*args, **kwargs):
            if not get_global_hiq_status():
                # print(f"👻 tau is disabled: {f.__name__}")
                # s.disable_hiq()
                return f(*args, **kwargs)
            # print(f"{f_name=}")
            f_name = f.__name__
            s.pre_processing(f_name, args, kwargs)
            result = None
            try:
                result = call_decorated(
                    f,
                    args,
                    kwargs,
                    tracing_type=os.environ.get("TRACE_TYPE", TRACING_TYPE_HIQ),
                )
            except Exception as e:
                s.handle_exception(f_name, e)
            s.post_processing(f_name)
            s.update_overhead()
            return result

        return __x

    def inserter_with_extra(s, extra=None, *_args, **_kwargs):
        def wrap(f):
            f_name = f.__name__
            tracing_type = os.environ.get("TRACE_TYPE", TRACING_TYPE_HIQ)

            def __x(*args, **kwargs):
                if not get_global_hiq_status():
                    print("👻 hiq is disabled (extra): {f_name}")
                    # s.disable_hiq()
                    return f(*args, **kwargs)
                s.pre_processing(f_name, args, kwargs, tree_extra=extra)
                result = None
                try:
                    result = call_decorated(f, args, kwargs, tracing_type=tracing_type)
                except Exception as e:
                    s.handle_exception(f_name, e)
                s.post_processing(f_name)
                s.update_overhead()
                return result

            return __x

        return wrap

    def enable_hiq(s, reset_trace=False):
        """Enable HiQ tracing

        Args:
            s (HiQBase): self object of HiQBase
            reset_trace (bool, optional): will the `s.tau` data structure will be reset to empty? Defaults to False.

        Returns:
            HiQBase: the current object itself
        """
        if s.enabled:
            return s
        try:
            if reset_trace:
                s.reset()
            if not get_global_hiq_status():
                print("🌚 global hiq switch is off")
                return s
            s.custom()
            for m, c, f, t in s.hiq_quadruple:
                s._h(m, c, f, t)
            s.enabled = True
        except ModuleNotFoundError as e:
            print(f"🦉 this module should be in the sys path. error: {e}")
        return s

    def disable_hiq(s, reset_trace=False):
        """Disable HiQ tracing

        Args:
            s (HiQBase): self object of HiQBase
            reset_trace (bool, optional): will the `s.tau` data structure will be reset to empty? Defaults to False.
        """
        if not s.enabled:
            return
        for module_name, class_name, func_name, tag in s.hiq_quadruple:
            class_func = f"{class_name}.{func_name}"
            if not class_name:
                class_func = func_name
            try:
                d = f"hiq.mod('{module_name}').{class_func} = s.o_{tag}"
                itree.exe(d, locals())
            except TypeError as e:
                s.__disable_c(module_name, class_name, func_name, tag)
        s.custom_disable()
        s.enabled = False
        if reset_trace:
            s.reset()

    def enable_c(s, module_name: str, class_name: str, func_name: str, new_func):
        _m = hiq.mod(module_name)
        _class = getattr(_m, class_name)
        _func_name = func_name
        _referents = gc.get_referents(_class.__dict__)[0]
        _original_val = _referents.get(_func_name, None)
        _referents[_func_name] = new_func
        _c = hiq.mod(EXTERNAL_C_MODULE)
        _c.pythonapi.PyType_Modified(_c.py_object(_class))
        return _original_val

    def __disable_c(s, module_name: str, class_name: str, func_name: str, tag: str):
        _m = hiq.mod(module_name)
        _class = getattr(_m, class_name)
        _func_name = func_name
        _referents = gc.get_referents(_class.__dict__)[0]
        d = f"_referents['{_func_name}'] = s.o_{tag}"
        itree.exe(d, locals())
        _c = hiq.mod(EXTERNAL_C_MODULE)
        _c.pythonapi.PyType_Modified(_c.py_object(_class))

    def reset(s):
        """reset the hiq map data structure to empty

        Args:
            s (HiQBase): self object of HiQBase
        """
        s.tau = collections.defaultdict(dict)
        s.check_oh_counter = 0

    def _h(s, module_name, class_name, func_name, tag: str = ""):
        try:
            class_func = f"{class_name}.{func_name}"
            if not class_name:
                class_func = func_name
            d = f"m_ = hiq.mod('{module_name}').{class_func}"
            itree.exe(d, locals())
            assert hasattr(locals()["m_"], "__call__"), "a callable is needed"
            if not tag:
                tag += str(s.count)
            # already defined in the custom
            if _is_callable(tag):
                d = f"""hiq.mod('{module_name}').{class_func} = {tag}"""
                itree.exe(d, locals())
            else:
                itree.exe(f"s.o_{tag} = m_", locals())
                spec_with_default, spec_wo_default = _get_full_argspecs(locals()["m_"])

                if inspect.ismethod(locals()["m_"]):
                    spec_with_default = spec_with_default[
                        spec_with_default.find(",") + 1 :
                    ]
                    spec_wo_default = spec_wo_default[spec_wo_default.find(",") + 1 :]
                    # spec_with_default += ",*args,**kwargs"
                    # spec_wo_default += ",*args,**kwargs"

                assert (
                    re.match(r"^[\w\.]+$", tag)
                    and ";" not in spec_with_default
                    and ";" not in spec_wo_default
                    and ";" not in module_name
                    and ";" not in class_func
                ), "no hacker"
                signature = spec_with_default
                if spec_with_default:
                    signature += ","
                if signature.startswith("**"):
                    signature = "s=s," + signature
                elif ",**" in signature:
                    i = signature.find(",**")
                    signature = signature[:i] + ",s=s" + signature[i:]
                else:
                    signature += "s=s"
                if signature.endswith(","):
                    signature = signature[:-1]
                if "." in class_func:
                    _class_name = class_func.split(".")[0]
                    _funct_name = class_func.split(".")[1]
                else:
                    _class_name = "🦉"
                    _funct_name = class_func
                if not s.itree_tpl:
                    raise Exception("empty tau tpl")
                d = s.itree_tpl.format(
                    tag=tag,
                    signature=signature,
                    spec_wo_default=spec_wo_default,
                    module_name=module_name,
                    _class_name=_class_name,
                    _funct_name=_funct_name,
                )
                d = d.replace(".🦉", "")
                if tag == HIQ_FUNC_PREFIX + HIQ_FUNC_DIO_RD:
                    d = d.replace("🐚", "s.dio_bytes_r += len(_r)")
                elif tag == HIQ_FUNC_PREFIX + HIQ_FUNC_DIO_WT:
                    d = d.replace("🐚", "s.dio_bytes_w += len(_r)")
                elif tag == HIQ_FUNC_PREFIX + HIQ_FUNC_SIO_RD:
                    d = d.replace("🐚", "s.sio_bytes_r += len(_r)")
                elif tag == HIQ_FUNC_PREFIX + HIQ_FUNC_SIO_WT:
                    d = d.replace("🐚", "s.sio_bytes_w += len(_r)")
                elif tag == HIQ_FUNC_PREFIX + HIQ_FUNC_NIO_GET:
                    d = d.replace(
                        "🐚",
                        "s.nio_bytes_r += len(_r.content) if (_r and _r.status_code < 400) else 0",
                    )
                elif tag == HIQ_FUNC_PREFIX + HIQ_FUNC_NIO_POS:
                    d = d.replace(
                        "🐚",
                        "s.nio_bytes_w += len(_r.content) if (_r and _r.status_code < 400) else 0",
                    )
                else:
                    d = d.replace("🐚", "")
                itree.exe(d, locals())
        except Exception as e:
            print(f"🦉 {module_name}.{class_name}.{func_name} is not traced({e})")
            if s.verbose:
                print(traceback.format_exc())
            # sys.exit(0)
        finally:
            s.count += 1

    def empty(s):
        return not s.tau

    def get_metrics(s, metrics_key=KEY_LATENCY) -> List[Tree]:
        r = []
        for k0 in s.tau:
            r.append(s.tau[k0][metrics_key])
        return r

    def get_k0s(s) -> List[str]:
        return s.tau.keys()

    def get_k0s_summary(s, metrics_key=KEY_LATENCY) -> List[Tuple]:
        ks = s.tau.keys()
        r = []
        for k0 in ks:
            t = s.tau[k0][metrics_key]
            t.consolidate()
            r.append((k0, t.root.span(), t.root.start, t.root.end))
        return r

    def get_metrics_by_k0(s, k0=None, metrics_key=KEY_LATENCY) -> Union[Tree, None]:
        return s.tau[k0][metrics_key] if k0 in s.tau else None

    def show(s, ignore_empty_tree=False, show_key=False, time_format=FORMAT_DATETIME):
        for k0 in s.tau:
            for k1 in s.tau[k0]:
                if not isinstance(s.tau[k0][k1], Tree):
                    continue
                s.tau[k0][k1].consolidate()
                span = abs(s.tau[k0][k1].root.span())
                # print(f"{span=:.9f}")
                if not ignore_empty_tree or span > 1e-6:
                    if show_key:
                        print(f"🔑 k0: {k0}, 🗝 k1: {k1}")
                    print(s.tau[k0][k1].get_graph(time_format=time_format))

    def get_overhead(s, format_=OverHeadFormat.ABS) -> float:
        """get tracing latency overhead in absolute format or percentage format

        Args:
            `format_` (str, optional): "abs" - output absolute value in milliseconds; otherwise, output in float point format: `overhead/total_latency`. Defaults to "abs".

        Returns:
            float: absolute value in micro-second, or a number between 0 and 1 which means the percentage of overhead over total latency.
        """
        if format_ == OverHeadFormat.ABS:
            return s.get_overhead_us()
        elif format == OverHeadFormat.PCT:
            return s.get_overhead_pct()
        else:
            raise ValueError(f"wrong format: {format_}")

    def get_overhead_us(s) -> float:
        """get tracing latency overhead in unit of micro-second

        How to calculate latency overhead? The latency overhead is attached to the latency tree. the latency overhead calculation is based on monotonic time and has unit of micro-second. When a HiQ system is instantiated, the initial overhead is 0. Every time a target function is called, we accumulate the overhead. When we finish a level-2 node in the HiQ tree, we update the `overhead` in the tree to get the final overhead of that trace.

        Returns:
            float: absolute value in micro-second
        """
        return s.overhead_us

    def get_overhead_pct(s) -> float:
        """get tracing latency overhead in percentage format

        Returns:
            float: a number between 0 and 1 which means the percentage of overhead over total latency.
        """
        total_latency = 0
        for k0 in s.tau:
            for k1 in s.tau[k0]:
                if k1 == KEY_LATENCY:
                    if itree.is_virtual_node(s.tau[k0][k1].root):
                        itree._itree.consolidate(s.tau[k0][k1].root)
                    tmp = s.tau[k0][k1].root.span()
                    if tmp == tmp:
                        total_latency += tmp
        if total_latency > 0:
            return s.overhead_us / (total_latency * 1e6)
        else:
            return -1

    @abstractmethod
    def custom(self):
        """The abstract method for customizing tracing logic"""

    @abstractmethod
    def custom_disable(self):
        """The abstract method for disabling customized tracing logic"""

    def __getstate__(self):
        self.get_tau_id = None
        a_state = itree.ForestStats.__getstate__(self)
        b_state = self.__dict__
        return (a_state, b_state)

    def __setstate__(self, state):
        a_state, b_state = state
        self.__dict__ = b_state
        itree.ForestStats.__setstate__(self, a_state)


class HiQLatency(HiQBase, Jack):
    """
    A convenient class for latency tracking

    Args:
        hiq_table_or_path (Union[str, List[Iterable[str]]], optional): this is an HiQ Conf, please refer to *HiQ Core Concepts* section in the HiQ documentation.Defaults to [].
        metric_funcs (List[Callable], optional): simple metric function with empty argument. Defaults to [time.time].
        hiq_id_func (Callable, optional): a callable to generate unique id for tau, the hiq map. Defaults to hiq.hiq_utils.get_tau_id.
        func_args_handler(Callable, optional): a callable to convert function args/kwargs into a string. Defaults to hiq.hiq_utils.func_args_handler.
        target_path (str, optional): the directory of the target code. Defaults to None.
        max_hiq_size (int, optional): the max size of hiq map. if the number is exceeded, tree will be sent to LMK. Defaults to 30.
        verbose (bool, optional): when verbose is true, more information will be recorded, like the full stack trace of exception will be recorded in HiQ tree node. Defaults to False.
        fast_fail (bool, optional): when it is true, raise exception to the upper level, don't swallow exceptions. Defaults to True.
        tpl (str, optional): hiq tpl path. Defaults to None.
        extra_hiq_table (List[str], optional): a list of string to decide to include metrics other than latency. Defaults to [].
        attach_timestamp (bool, optional): for non-time/non-latency metric tree, should we attach start, end timestamps in the extra dictionary? Defaults to False.
        extra_metrics (set, optional): metrics to track in `extra` field of HiQ node. The value could be EXTRA_METRIC_ARGS, EXTRA_METRIC_FILE or EXTRA_METRIC_FUNC and it is normally used in development environment. Defaults to set().

    Raises:
        ValueError: Requires the input is valid

    Example usage:

    >>> from hiq.base import HiQLatency
    >>> trace = HiQLatency()
    """

    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        HiQBase.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=hiq_id_func,
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )
        Jack.__init__(sf)

    def custom(sf):
        pass

    def custom_disable(sf):
        pass


class HiQMemory(HiQBase, Jack):
    """
    A convenient class for RSS(resident set size) of memory tracking. Unit of memory is MB.

    RSS is the portion of memory occupied by a process that is held in main memory (RAM). The rest of the occupied memory exists in the swap space or file system, either because some parts of the occupied memory were paged out, or because some parts of the executable were never loaded.

    Args:
        hiq_table_or_path (Union[str, List[Iterable[str]]], optional): this is an HiQ Conf, please refer to *HiQ Core Concepts* section in the HiQ documentation.Defaults to [].
        metric_funcs (List[Callable], optional): simple metric function with empty argument. Defaults to [time.time, get_memory_mb].
        hiq_id_func (Callable, optional): a callable to generate unique id for tau, the hiq map. Defaults to hiq.hiq_utils.get_tau_id.
        func_args_handler(Callable, optional): a callable to convert function args/kwargs into a string. Defaults to hiq.hiq_utils.func_args_handler.
        target_path (str, optional): the directory of the target code. Defaults to None.
        max_hiq_size (int, optional): the max size of hiq map. if the number is exceeded, tree will be sent to LMK. Defaults to 30.
        verbose (bool, optional): when verbose is true, more information will be recorded, like the full stack trace of exception will be recorded in HiQ tree node. Defaults to False.
        fast_fail (bool, optional): when it is true, raise exception to the upper level, don't swallow exceptions. Defaults to True.
        tpl (str, optional): hiq tpl path. Defaults to None.
        extra_hiq_table (List[str], optional): a list of string to decide to include metrics other than latency. Defaults to [].
        attach_timestamp (bool, optional): for non-time/non-latency metric tree, should we attach start, end timestamps in the extra dictionary? Defaults to False.
        extra_metrics (set, optional): metrics to track in `extra` field of HiQ node. The value could be EXTRA_METRIC_ARGS, EXTRA_METRIC_FILE or EXTRA_METRIC_FUNC and it is normally used in development environment. Defaults to set().

    Raises:
        ValueError: Requires the input is valid

    Example usage:

    >>> from hiq.base import HiQMemory
    >>> trace = HiQMemory()
    """

    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time, get_memory_mb],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),  # EXTRA_METRIC_FILE
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        HiQBase.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=hiq_id_func,
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )
        Jack.__init__(sf)

    def custom(sf):
        pass

    def custom_disable(sf):
        pass


HiQSimple = HiQLatency

if __name__ == "__main__":
    import pickle
    from multiprocessing import Process, Queue, Lock

    def get_tau_id_():
        return 1

    h1 = HiQLatency(fast_fail=1, hiq_id_func=get_tau_id_)
    h1.tau[0] = {"hello": Tree(extra={}, tid="simon", queue_lmk=Queue())}
    h1.tau[1] = {"hello": Tree(extra={}, tid="simon", queue_lmk=None)}
    h1.tau[2] = {"hello": 123}

    d = pickle.dumps(h1)
    print(d)
    h2 = pickle.loads(d)
    d2 = pickle.dumps(h2)
    # print(d2)
    print(d == d2)

    # print(h1.tau)
    print(type(h2))
    print(h2.tau)
    print(type(h1.tau[0]["hello"]))
    print(type(h2.tau[0]["hello"]))
    print(h1.tau[0]["hello"].queue_lmk)
    print(h2.tau[0]["hello"].queue_lmk)
    h2.show()
