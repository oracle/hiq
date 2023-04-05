# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import psutil
import os
from hiq.utils import read_file, execute_cmd

# Process Level


def get_memory_gb() -> float:
    return psutil.Process().memory_info().rss / (1 << 30)


def get_memory_mb() -> float:
    """Get RSS in MB unit

    Returns:
        float: RSS of current process in MB
    """
    return psutil.Process().memory_info().rss / (1 << 20)


def get_memory_kb() -> float:
    return psutil.Process().memory_info().rss / 1024


def get_memory_b() -> float:
    return psutil.Process().memory_info().rss


# System Level


def get_system_peak_memory() -> int:
    try:
        if "KUBERNETES_SERVICE_HOST" in os.environ:
            return int(
                read_file(
                    "/sys/fs/cgroup/memory/memory.max_usage_in_bytes", by_line=False
                )
            )
    except:
        pass
    return -1


def get_system_memory_usage() -> int:
    try:
        if "KUBERNETES_SERVICE_HOST" in os.environ:
            return int(
                read_file("/sys/fs/cgroup/memory/memory.usage_in_bytes", by_line=False)
            )
        else:
            return psutil.virtual_memory()[3]
    except:
        pass
    return -1


# GPU

try:
    import importlib

    pynvml = importlib.import_module("pynvml")
    if pynvml:
        pynvml.nvmlInit()
except:
    pynvml = None

gpu_idx = os.environ.get("CUDA_VISIBLE_DEVICES", None)


def total_gpu_memory_mb_nvidia_smi():
    """
    The built-in sensors queried by nvidia-smi are not highly accurate, individually calibrated, devices. An error margin of +/- 5% should be assumed.
    # unit is MiB
    """
    cmd = "nvidia-smi --query-gpu=memory.used --format=csv,nounits,noheader"
    if gpu_idx is not None:
        cmd += f" -i {gpu_idx}"
    output = execute_cmd(cmd, verbose=False)
    return sum([int(x) for x in output])


def total_gpu_memory_mb_nvml():
    if gpu_idx:
        cuda_indices = [int(x) for x in gpu_idx.split(",")]
    else:
        cuda_indices = range(pynvml.nvmlDeviceGetCount())
    gpu_usage_mb = [
        pynvml.nvmlDeviceGetMemoryInfo(pynvml.nvmlDeviceGetHandleByIndex(i)).used
        // (2**20)
        for i in cuda_indices
    ]
    return sum(gpu_usage_mb)


total_gpu_memory_mb = (
    total_gpu_memory_mb_nvml if pynvml else total_gpu_memory_mb_nvidia_smi
)
