# HiQ version 1.0.
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/ 
#

__author__ = "Fuheng Wu<fuheng.wu@oralce.com>"
__date__ = "2022-09-28"
__doc__ = "HiQ is a declarative, non-intrusive, dynamic and transparent tracking and optimization system"
__version__ = "1.0.4"
__credits__ = "Henry Wu, Ivan Davchev, Jun Qian"

import sys

vinfo = sys.version_info
if vinfo.major < 3 or (vinfo.major == 3 and vinfo.minor < 8):
    print(f"HiQ supports Python version 3.8 and higher. Your version is {vinfo.major}.{vinfo.minor}.")
    sys.exit(1)

from .hiq_utils import (
    set_global_hiq_status,
    get_global_hiq_status,
    HiQStatusContext,
)
from .utils import (
    SingletonMeta,
    SingletonBase,
    memoize,
    memoize_first,
    lmk_data_handler,
    is_hiqed,
    get_env_bool,
    get_env_int,
    get_env_float,
    get_proxies,
    SilencePrint,
    random_str,
    download_from_http,
    ensure_folder,
    write_file,
    read_file,
    ts_pair_to_dt,
    ts_to_dt,
    utc_to_pst,
    execute_cmd,
    get_home,
    create_gantt_chart_time,
    create_gantt_chart_memory
)
from .tree import (
    get_duration_from_hiq_string,
    get_graph_from_string,
    Tree
)

try:
    from .memory import (
        get_memory_mb,
        get_memory_kb,
        get_memory_b,
    )
except ImportError:
    pass
from .base import HiQLatency, HiQSimple, HiQMemory
from .server_flask import HiQFlaskLatency, HiQFlaskMemory, HiQFlaskLatencyOtel
from .server_fastapi import HiQFastAPILatency, HiQFastAPILatencyMixin, HiQFastAPIMemory, run_fastapi
from .constants import *
from .ddict import *

try:
    from itree import mod
except ImportError:
    pass

__all__ = [
    "HiQLatency",
    "HiQFlaskLatency",
    "HiQFlaskMemory",
    "HiQFlaskLatencyOtel",
    "HiQFastAPILatency",
    "HiQFastAPIMemory",
    "HiQFastAPILatencyMixin",
    "run_fastapi",
    "HiQSimple",
    "HiQMemory",
    "HiQStatusContext",
    "get_global_hiq_status",
    "set_global_hiq_status",
    "SingletonMeta",
    "SingletonBase",
    "memoize",
    "memoize_first",
    "lmk_data_handler",
    "is_hiqed",
    "get_env_bool",
    "get_env_int",
    "get_env_float",
    "get_proxies",
    "SilencePrint",
    "random_str",
    "download_from_http",
    "ensure_folder",
    "write_file",
    "read_file",
    "get_memory_mb",
    "get_memory_kb",
    "get_memory_b",
    "ts_pair_to_dt",
    "ts_to_dt",
    "utc_to_pst",
    "execute_cmd",
    "get_home",
    "get_duration_from_hiq_string",
    "get_graph_from_string",
    "Tree",
    "create_gantt_chart_time",
    "create_gantt_chart_memory"
]
