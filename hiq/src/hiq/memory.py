# HiQ version 1.0.
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/ 
#

import psutil


def get_memory_mb() -> float:
    """Get RSS in MB unit

    Returns:
        float: RSS of current process in MB
    """
    return psutil.Process().memory_info().rss / (1024 * 1024)


def get_memory_kb() -> float:
    return psutil.Process().memory_info().rss / 1024


def get_memory_b() -> float:
    return psutil.Process().memory_info().rss
