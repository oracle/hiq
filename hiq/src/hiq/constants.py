# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

from enum import Enum

EXTRA_START_TIME_KEY = "start"
EXTRA_END_TIME_KEY = "end"

TREE_ROOT_NAME = "root"
FORMAT_TIMESTAMP = "_timestamp_"
FORMAT_DATETIME = "_datetime_"

HIQ_FUNC_PREFIX = "__"

HIQ_FUNC_DIO_RD = "dio_r"
HIQ_FUNC_DIO_WT = "dio_w"

HIQ_FUNC_SIO_RD = "sio_r"
HIQ_FUNC_SIO_WT = "sio_w"

HIQ_FUNC_NIO_GET = "nio_get"
HIQ_FUNC_NIO_POS = "nio_pos"

TAU_TABLE_DIO_RD = ["_io", "TextIOWrapper", "read", HIQ_FUNC_DIO_RD]
TAU_TABLE_DIO_WT = ["_io", "TextIOWrapper", "write", HIQ_FUNC_DIO_WT]

HIQ_TABLE_SIO_RD = ["os", "", "read", HIQ_FUNC_SIO_RD]
HIQ_TABLE_SIO_WT = ["os", "", "write", HIQ_FUNC_SIO_WT]

TAU_TABLE_NIO_GET = ["requests", "", "get", HIQ_FUNC_NIO_GET]
TAU_TABLE_NIO_POS = ["requests", "", "post", HIQ_FUNC_NIO_POS]

KEY_LATENCY = "time"
KEY_MEMORY = "get_memory_mb"

KEY_EXC_SUM = "exception_summary"
KEY_EXC_TRA = "exception_trace"

TAU_TPL_LOC = "data/tau.tpl"
TAU_PKL_LOC = "data/tau.pk"

TS_LEN = len(str(1631339134.691))  # 14

EXTERNAL_C_MODULE = "ctypes"

TRACING_TYPE_HIQ = "oci-hiq"
TRACING_TYPE_OCI = "oci-apm"
TRACING_TYPE_OTM = "opentelemetry"
TRACING_TYPE_PROM = "prometheus"

# 1 Page, 32K slots for our hash table
HIQ_SHARED_MEMORY = 1024 * 4
GLOBAL_HIQ_TTL_S = 60

HIQ_C_SET = {"_io.TextIOWrapper.read", "_io.TextIOWrapper.write"}


class ExtraMetrics(Enum):
    ARGS = 1
    FILE = 2
    FUNC = 3


class OverHeadFormat(Enum):
    ABS = 1
    PCT = 2
