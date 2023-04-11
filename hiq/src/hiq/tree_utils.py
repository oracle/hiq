# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import io
from hiq.node_utils import __peek_tree
from hiq.node_utils import _pp_tree
from hiq.constants import *
from typing import Tuple


def split_extra(s: str) -> Tuple[str, str]:
    """
    Returns:
        tree_extra, pure tree
    """
    if not s.startswith("v"):
        return None, s
    else:
        s = s[s.index(",") + 1 :]
        run_length = int(s[: s.index(",")])
        s = s[s.index(",") + 1 :]
        return s[:run_length], s[run_length:]
