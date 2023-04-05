# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

from hiq.http_metric_client import HttpMetricsClient


class OciT2Client(HttpMetricsClient):
    """
    OciT2Client is a class for transmitting metrics to Oracle T2

    Examples:

    .. highlight:: python
    .. code-block:: python

        from hiq.vendor_oci_t2 import OciT2Client as Client
        from time import monotonic

        client = Client(url=...)
        METRIC_NAME = "hiq.predict"
        metric = Client.metric_calc_delta(f"{METRIC_NAME}.success", start_time=monotonic())
        metrics_queue.put_nowait(metric)
        #...
        retry_count=1
        client.gauge_metric("operation_retry_count", retry_count)
        client.submit_metrics_queue()

    """
