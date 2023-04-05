# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

"""A generic node for HiQ tree

Node in HiQ has `start` and `end` property. They can be anything that happens at start/end time,
including time itself, and CPU memory usage, GPU memory usage, io traffic by bytes etc.

extra is a dictionary to record extra information.
"""

import itree

Node = itree.Node
is_virtual_node = itree.is_virtual_node

if __name__ == "__main__":
    n = Node("", 0, 0)
    print(n)
