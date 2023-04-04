# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import os
import json
import syslog
import time
import requests
import urllib3
from hiq.utils import read_file
import queue


urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)
# Suppress warnings about deprecated use of certificate common name.
# RFC-2818 deprecated the CN field in server certificates, but it's still
# the most common way to indicate the server hostname. The openssl tool
# makes it ridiculously difficult to use the SAN field (the recommended
# alternative), and support for SAN across various systems seems sketchy,
# at best. The Python maintainers have decided that it's worth a nasty
# runtime warning. We don't agree with that, so I've added this line.
import datetime


def __emit_log(sev, msg):
    """
    Emit a log to stdout. sev should be a syslog error level; msg can be any
    text string.
    """
    print(datetime.datetime.now().isoformat(), sev, msg)


class HttpMetricsClient(object):
    """
    HttpMetricsClient is a generic class for transmitting metrics to any metrics server by HTTP

    This includes the config needed to create and submit metrics, along with the requests.Session we use to send the data.

    Examples:

    .. highlight:: python
    .. code-block:: python

        from hiq.http_metric_client import HttpMetricsClient as Client
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

    @staticmethod
    def metric_calc_delta(metric, start_time):
        """Send a metric with a time measurement"""
        end_time = time.monotonic()
        delta = round((end_time - start_time) * 1000)
        metric_data = {
            "name": metric,
            "datapoints": [
                {"timestamp": int(round(time.time() * 1000)), "value": delta}
            ],
        }
        return metric_data

    def __init__(
        self,
        url,
        ad_longform=None,
        metrics_queue=None,
        trusted_cert=None,
        project="hiq",
        timeout=5,
    ):
        """Constructor

        Parameters:
            url: The metrics data server URL
            ad_longform: the long-form name of the availability domain of the style like `eu-frankfurt-ad-1`
            metrics_queue: a Python queue.Queue object used for queuing metrics
            trusted_cert: The filename of the root certificate for authenticating the server, if needed
        """
        self.conf = {}
        self.conf["hostname"] = read_file("/etc/hostname", by_line=False, strip=True)
        region = read_file("/etc/region", by_line=False, strip=True)
        self.conf["region"] = region if region else "none"
        self.conf["ad_longform"] = ad_longform
        self.conf["url"] = url
        self.metrics_queue = metrics_queue if metrics_queue else queue.Queue()
        if not trusted_cert or not os.path.exists(trusted_cert):
            trusted_cert = "/etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt"
        self.trusted_cert = trusted_cert if os.path.exists(trusted_cert) else None
        self.timeout = timeout
        self.project = project

    def timing_metric_data(self, metric_data):
        """Send a list of metrics server

        :param metric_data list of metrics
        """
        info = self.wrap_metric_data(metric_data=metric_data)

        try:
            resp = requests.put(
                f'{self.conf["url"]}aggregation',
                timeout=self.timeout,
                json=info,
                verify=self.trusted_cert,
            )
        except requests.exceptions.ConnectionError as err:
            __emit_log(syslog.LOG_ERR, f"network connection error: {err}")
        else:
            if resp.status_code < 200 or resp.status_code >= 300:
                __emit_log(
                    syslog.LOG_ERR, f"server status error: {resp} {info} {resp.text}"
                )

    def wrap_metric_data(self, metric_data) -> dict:
        """
        package up metrics in the data structure metrics server wants

        :param metric_data: info['metrics'] => list of metrics
        :return: info (metric dict/json)
        """
        info = {
            "project": self.project,
            "hostname": self.conf["hostname"],
            "region": self.conf["region"],
            "availabilityDomain": self.conf["ad_longform"],
            "metrics": metric_data,
        }
        if fleet := os.getenv("T2_FLEET", ""):
            info["fleet"] = fleet
        return info

    def submit_metrics_queue(self):
        """drain metrics_queue and submit the metrics to server"""
        metric_data = list(self.metrics_queue.queue)
        if not metric_data:
            msg = "metric_data must not be empty!"
            raise ValueError(msg)
        self.timing_metric_data(metric_data=metric_data)
        # handy for peeking at request to server and metric_data
        # __emit_log(syslog.LOG_DEBUG,
        #          f'json: {json.dumps(self.wrap_metric_data(metric_data))}')

    def gauge_metric(self, metric, value):
        """emit a gauge metric with the given name and value."""
        metric_data = {
            "name": metric,
            "datapoints": [
                {"timestamp": int(round(time.time() * 1000)), "value": value}
            ],
        }
        self.metrics_queue.put_nowait(metric_data)

    def timing_metric(self, metric: str, start_time: int):
        """
        convenience method to calculate a time delta for a metric and also put it in the metrics_queue

        :param metric: metric name
        :param start_time: start time in millisecond unit
        """
        metric_data = self.metric_calc_delta(metric, start_time)
        self.metrics_queue.put_nowait(metric_data)

    def get(self, query, params=None):
        """
        method for mock metrics server API during testing, not applicable to prod
        """
        resp = requests.get(
            f'{self.conf["url"]}{query}',
            params=params,
            timeout=self.timeout,
            verify=self.trusted_cert,
        )
        try:
            return json.loads(resp.text), resp.headers
        except json.JSONDecodeError:
            msg = (
                "Failed to parse query response: "
                + f'{self.conf["url"]}{query} '
                + f"{repr(params)} "
                + f"(response code = {str(resp.status_code)})"
            )
            raise IOError(msg)


if __name__ == "__main__":
    o = HttpMetricsClient(url="", ad_longform="")
