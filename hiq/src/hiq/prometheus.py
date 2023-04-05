# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

from prometheus_client import Summary, push_to_gateway, CollectorRegistry, Counter
from hiq.utils import memoize_first
import asyncio


@memoize_first
def get_summary(name, desc=None):
    if name[0:2] == "__":
        name = "hiq_" + name[2:]
    return Summary(name, name if desc is None else desc)


"""
class GatewayClient:
    #https://stackoverflow.com/questions/61785170/how-can-i-expose-prometheus-metrics-from-multiple-subprocesses
    def __init__(self, addr, thing_id):
        self.gateway_address = addr
        self.job_id = "thing-{}".format(thing_id)
        self.registry = CollectorRegistry()
        # define metrics etc
        self.some_counter = Counter('some_counter', 'A counter', registry=self.registry)

    async def start(self):
        while True:
            # push latest data
            push_to_gateway(self.gateway_address, job=self.job_id, registry=self.registry
            await asyncio.sleep(15)

    # methods to set metrics etc
    def inc_some_counter(self):
        self.some_counter.inc()
"""
