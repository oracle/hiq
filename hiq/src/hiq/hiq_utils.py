# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import contextvars
import gc
import os
import re
import time
from multiprocessing import resource_tracker, shared_memory
from typing import *

from cachetools import TTLCache, cached

from hiq.constants import *
from hiq.ddict import ddjson
from hiq.utils import get_env_bool

DEFAULT_HIQ_STATUS = get_env_bool("HIQ_ENABLED", True)
HIQ_STATUS_CACHED = get_env_bool("HIQ_STATUS_CACHED", False)


def __remove_shm_from_resource_tracker():
    """Monkey-patch multiprocessing.resource_tracker so SharedMemory won't be tracked

    More details at: https://bugs.python.org/issue38119
    """
    from multiprocessing import Process, resource_tracker
    from multiprocessing.shared_memory import SharedMemory

    def fix_register(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.register(self, name, rtype)

    resource_tracker.register = fix_register

    def fix_unregister(name, rtype):
        if rtype == "shared_memory":
            return
        return resource_tracker._resource_tracker.unregister(self, name, rtype)

    resource_tracker.unregister = fix_unregister

    if "shared_memory" in resource_tracker._CLEANUP_FUNCS:
        del resource_tracker._CLEANUP_FUNCS["shared_memory"]


def set_global_hiq_status(on=True, name="hiq", debug=False):
    """Set the global HiQ status. True is to enable HiQ, and False disable.

    >>> import hiq
    >>> hiq.get_global_hiq_status()
    True
    >>> hiq.set_global_hiq_status(0)
    😇 set global hiq to 0
    >>> hiq.get_global_hiq_status()
    False
    """
    try:
        c = shared_memory.ShareableList(name=name)
        c[0] = on
        if debug:
            print(f"😇 set global hiq to {on}")
    except FileNotFoundError:
        __remove_shm_from_resource_tracker()
        c = shared_memory.ShareableList([on], name=name)
        resource_tracker.unregister(name, "shared_memory")
        if debug:
            print(f"😤 set global hiq to {on}")
    except PermissionError as e:
        return False
    except Exception as e:
        raise e


def get_global_hiq_status(name="hiq", default=DEFAULT_HIQ_STATUS) -> bool:
    """Get the global HiQ status. True means HiQ is enabled, and False disabled.

    When `HIQ_STATUS_CACHED` is set as True, the global hiq status will be cached for 5 seconds. Otherwise, it will read shared memory.

    >>> import hiq
    >>> hiq.get_global_hiq_status()
    False
    >>> hiq.set_global_hiq_status(1)
    😇 set global hiq to 1
    >>> hiq.get_global_hiq_status()
    True
    """
    if HIQ_STATUS_CACHED:
        return _get_global_hiq_on_cached(name, default)
    return _get_global_hiq_on(name, default)


# cache data for no longer than 2 minutes
@cached(cache=TTLCache(maxsize=1024, ttl=GLOBAL_HIQ_TTL_S))
def _get_global_hiq_on_cached(name="hiq", default=DEFAULT_HIQ_STATUS):
    """
    time cost: 102.04315185546875 us.
    """
    try:
        return bool(shared_memory.ShareableList(name=name)[0])
    except FileNotFoundError as e:
        return default
    except Exception as e:
        raise e


def _get_global_hiq_on(name="hiq", default=DEFAULT_HIQ_STATUS):
    """
    time cost: 102.04315185546875 us.
    """
    try:
        return bool(shared_memory.ShareableList(name=name)[0])
    except (FileNotFoundError, PermissionError) as e:
        return default
    except Exception as e:
        raise e


class HiQStatusContext(object):
    """An HiQ context manager

    Inside HiQStatusContext, HiQ status is always enabled unless the status is changed in other processes(HiQ status is not guarded).

    >>> from hiq import HiQStatusContext
    >>> with HiQStatusContext():
            # HiQ will be enabled inside the `with` block, and reverted to original value out of the block
    >>> with HiQStatusContext(target_status_on=False):
            # HiQ will be disabled inside the `with` block, and reverted to original value out of the block
    """

    def __init__(self, target_status_on=True, debug=False):
        """Constructor of HiQStatusContext

        Args:
            target_status_on (bool, optional): set the target HiQ status you want to set in the context manager. Defaults to True.
            debug (bool, optional): print more information when debug is True. Defaults to False.
        """
        self.original_hiq_status = get_global_hiq_status()
        self.target_on = target_status_on
        self.set = False
        self.debug = debug

    def __enter__(self):
        if self.original_hiq_status != self.target_on:
            set_global_hiq_status(self.target_on, debug=self.debug)
            self.set = True

    def __exit__(self, type, value, traceback):
        if self.set:
            set_global_hiq_status(self.original_hiq_status, debug=self.debug)


def read_csv_to_list(file_path):
    res = []
    # CSV
    import csv

    try:
        with open(file_path, mode="r", encoding="utf-8") as csvfile:
            spamreader = csv.reader(
                csvfile,
                delimiter=",",
                quotechar='"',
                doublequote=True,
                skipinitialspace=True,
            )
            for row in spamreader:
                res.append(row)
        return res
    except Exception as e:
        return []


def get_hiq_table(hiq_table_or_path):
    if isinstance(hiq_table_or_path, str):
        if not os.path.exists(hiq_table_or_path):
            raise Exception(f"😓 file {hiq_table_or_path} doesn't exist.")
        res = []
        # JSON
        try:
            data = ddjson(hiq_table_or_path)
            for d in data:
                res.append([d.o_module, d.o_class, d.o_function, d.o_name])
            return res
        except ValueError as e:
            pass
        return read_csv_to_list(hiq_table_or_path)
    elif isinstance(hiq_table_or_path, list):
        return hiq_table_or_path
    else:
        raise Exception(f"bad data:{hiq_table_or_path}")


def _is_callable(a_: str):
    if not re.match(r"^[\w\.]+$", a_):
        raise Exception(f"wrong input {a_}")
    try:
        exec(f"_exist = callable({a_})", globals(), locals())
    except NameError:
        return 0
    return locals()["_exist"]


def silent_import(module_name: str):
    try:
        import importlib

        return importlib.import_module(module_name)
    except:
        return None


np = silent_import("numpy")
torch = silent_import("torch")
pandas = silent_import("pandas")

nnmodule_to_params = {}


def nnmodule_to_str(a):
    global nnmodule_to_params
    if id(a) in nnmodule_to_params:
        num_params = nnmodule_to_params[id(a)]
    else:
        num_params = sum(p.numel() for p in a.parameters())
        nnmodule_to_params[id(a)] = num_params
    return f"{a._get_name()}({num_params})"


def __value_to_str(i, depth=1):
    if depth == 3:
        return "..."
    s = ""
    if i is None:
        s += "None"
    elif isinstance(i, str):
        s += f"str({i[:100]})"
        if len(i) > 100:
            s += "..."
    elif isinstance(i, bytes):
        s += f"bytes({len(i)})"
    elif np and isinstance(i, np.ndarray):
        s += f"ndarry{str(i.shape).replace(' ', '')}"
    elif isinstance(i, dict):
        tmp = []
        for k, v in list(i.items())[:3]:
            tmp.append(__value_to_str(v, depth + 1))
        if len(i.items()) > 3:
            s += f"dict(k:{list(i.keys())[:3]}...,v:{tmp}...)"
        else:
            s += f"dict(k:{list(i.keys())},v:{tmp})"
    elif isinstance(i, list):
        tmp = []
        for idx, e in enumerate(i):
            tmp.append(__value_to_str(e, depth + 1))
            if idx == 10:
                tmp.append("...")
                break
        s += f"list({len(i)},{','.join(tmp)})"
    elif torch and isinstance(i, torch.Tensor):
        s += f"tensor({str(i.shape).replace(' ', '')})"
    elif torch and isinstance(i, torch.nn.Module):
        s += f"nn({nnmodule_to_str(i)})"
    elif pandas and isinstance(i, pandas.core.frame.DataFrame):
        s += f"pandas({str(i.shape).replace(' ', '')})"
    else:
        if hasattr(i, "__len__"):
            s += f"{type(i).__name__}({str(len(i))})"
        else:
            s += f"{type(i).__name__}({i})"
    return s


def __func_arguments_str(args: List[Any]) -> str:
    """
    Tracing large data structure like arrays could be a performance killer. It will take a lot of CPU and some memory as well, and slow down the program.

    There are three ways to handle it:

    - Log a summary (default behavior): By default, if you log an array with size > 10,000, HiQ will only log the first 10,000 values, along with the shape.
    - Omit the array: You can also just choose not to log the array at all.
    - Manual transformation: .

    Args:
        args (List[Any]): the function arguments

    Returns:
        str : a string representation of the arguments
    """

    arg_list = []
    for i in args:
        arg_list.append(__value_to_str(i))
    return ",".join(arg_list)


def __func_kwargs_str(kwargs: Dict[str, Any]) -> str:
    r = {}
    for k, v in kwargs.items():
        r[k] = __value_to_str(v)
    return str(r)


def func_args_handler(x: Any, func_name=None) -> str:
    if isinstance(x, tuple):
        return __func_arguments_str(x)
    elif isinstance(x, dict):
        return __func_kwargs_str(x)
    raise ValueError(f"input has wrong type: {type(x)}")


def call_decorated(f: Callable, args=None, kwargs=None, tracing_type=TRACING_TYPE_HIQ):
    """Call with tracing type: HIQ or OCI

    HIQ is to build the HiQTree and then output or send to agent.
    OCI is to collect span and send data to OCI APM server.

    HIQ is the default way for monolithic application. OCI APM sends data in the same thread so it has longer latency but it is better for distributed applications.

    """
    if not args:
        args = {}
    if not kwargs:
        kwargs = {}
    if tracing_type == TRACING_TYPE_HIQ:
        return f(*args, **kwargs)
    elif tracing_type == TRACING_TYPE_OCI:
        from py_zipkin.zipkin import zipkin_span

        with zipkin_span(
            service_name=os.environ.get("SERVICE_NAME", "hiq"),
            span_name=f.__name__,
        ):
            return f(*args, **kwargs)
    elif tracing_type == TRACING_TYPE_OTM:
        from opentelemetry import trace

        tracer_name = os.environ.get("OTM_TRACER_NAME", "otm_hiq")
        tracer = trace.get_tracer(tracer_name)
        with tracer.start_as_current_span(f.__name__):
            return f(*args, **kwargs)
    elif tracing_type == TRACING_TYPE_PROM:
        from hiq.prometheus import get_summary

        with get_summary(f.__name__).time():
            return f(*args, **kwargs)

    else:
        return f(*args, **kwargs)


SERVER_NAME = "flask"
flask_dependency_ok = True


def get_tau_id(server_name=None):
    global flask_dependency_ok
    if server_name == SERVER_NAME and flask_dependency_ok:
        try:
            from flask import has_request_context, request

            tau_id = None
            if has_request_context():
                tau_id = request.environ.get("HTTP_X_REQUEST_ID")
            return tau_id
        except:
            flask_dependency_ok = False
            pass
    return None


# import cvpickle
class HiQIdGenerator(object):
    counter = 0

    def __init__(self):
        import itree

        self.context_var = contextvars.ContextVar("🆔")
        # cvpickle.register_contextvar(self.context_var, __name__)
        self.context_var.set(str(itree.time_us()) + str(HiQIdGenerator.counter % 10))
        HiQIdGenerator.counter += 1

    def __call__(self):
        return str(self.context_var.get())


class FlaskReqIdGenerator(object):
    def __call__(self):
        from flask import has_request_context, request

        return (
            request.environ.get("HTTP_X_REQUEST_ID")
            if has_request_context()
            else "flask-req"
        )


get_global_hiq_status()

if __name__ == "__main__":
    start = time.perf_counter()
    tau_on = get_global_hiq_status()
    end = time.perf_counter()
    print(f"time cost: {(end - start) * 1e6}us, {tau_on}")
    for i in range(20):
        o = HiQIdGenerator()
        print(o())
