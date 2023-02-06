# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/ 
#

import psutil
import os
from hiq.utils import read_file

# Process Level

def get_memory_gb() -> float:
    return psutil.Process().memory_info().rss / (1<<30)


def get_memory_mb() -> float:
    """Get RSS in MB unit

    Returns:
        float: RSS of current process in MB
    """
    return psutil.Process().memory_info().rss / (1<<20)


def get_memory_kb() -> float:
    return psutil.Process().memory_info().rss / 1024


def get_memory_b() -> float:
    return psutil.Process().memory_info().rss


# System Level

def get_system_peak_memory() -> int:
    try:
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            return int(read_file('/sys/fs/cgroup/memory/memory.max_usage_in_bytes', by_line=False))
    except:
        pass
    return -1


def get_system_memory_usage() -> int:
    try:
        if 'KUBERNETES_SERVICE_HOST' in os.environ:
            return int(read_file('/sys/fs/cgroup/memory/memory.usage_in_bytes', by_line=False))
        else:
            return psutil.virtual_memory()[3]
    except:
        pass
    return -1
