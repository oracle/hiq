# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import time
import requests
import os

from py_zipkin import Encoding
from py_zipkin.zipkin import zipkin_span


def get_oci_apm_endpoint(APM_BASE_URL="", key=""):
    endpoint = os.environ.get("APM_BASE_URL", APM_BASE_URL)
    key = os.environ.get("APM_PUB_KEY", key)  # "JL6DVW2YBYYPA6G53UG3ZNNEN642AKPA"
    API_VER = os.environ.get("APM_API_VER", "20200101")

    final_endpoint = f"{endpoint}/{API_VER}/observations/public-span?dataFormat=zipkin&dataFormatVersion=2&dataKey={key}"
    if not key:
        raise ValueError("🦉 Please setup environment variable `APM_PUB_KEY`")
    if not endpoint:
        raise ValueError("🦉 Please setup environment variable `APM_BASE_URL`")
    return final_endpoint


class OciApmHttpTransport(object):
    """a zipkin transport_handler class to emit traces to Oracle APM

    To make it work, you need to set two environment variables: `APM_BASE_URL`, `APM_PUB_KEY`

    Example:

    .. highlight:: python
    .. code-block:: python

        import time

        from py_zipkin import Encoding
        from py_zipkin.zipkin import zipkin_span
        from hiq.vendor_oci_apm import OciApmHttpTransport


        def fun():
            with zipkin_span(
                service_name="hiq_test_apm",
                span_name="fun_test",
                transport_handler=OciApmHttpTransport,
                encoding=Encoding.V2_JSON,
                binary_annotations={"mode": "sync"},
                sample_rate=100,
            ):
                time.sleep(5)
                print("hello")


        if __name__ == "__main__":
            fun()

    """

    def __init__(s, encoded_span, apm_url=None, debug=False):
        if apm_url is None:
            apm_url = get_oci_apm_endpoint()
        s.encoded_span = encoded_span
        s.apm_url = apm_url
        s.debug = debug
        s.call()

    def call(s):
        if s.debug:
            start = time.monotonic()
        res = requests.post(
            s.apm_url,
            data=s.encoded_span,
            headers={"Content-Type": "application/json"},
        )
        if s.debug:
            print(f"😎 {len(s.encoded_span)=}")
            end = time.monotonic()
            post_latency_cost = (end - start) * 1e6
            print(f"⏰ {post_latency_cost=}us, {res.status_code=}")


class HiQOciApmContext(zipkin_span):
    """Logs a root zipkin span with HiQ support

    Example:

    .. highlight:: python
    .. code-block:: python

        import time

        from hiq.vendor_oci_apm import HiQOciApmContext


        def fun():
            with HiQOciApmContext(
                service_name="hiq_test_apm", span_name="fun_test",
            ):
                time.sleep(5)
                print("hello")


        if __name__ == "__main__":
            fun()
    """

    def __init__(
        self,
        service_name="hiq_service_name",
        span_name="hiq_span_name",
        binary_annotations={"mode": "sync"},
        sample_rate=100,
    ):
        """Constructor of HiQOciApmContext class

        Args:
            service_name (str, optional): The name of the called service. Defaults to "hiq_service_name".
            span_name (str, optional): root span name. Defaults to "hiq_span_name".
            binary_annotations (dict, optional): dict of str -> str span attrs. Defaults to {"mode": "sync"}.
            sample_rate (int, optional): Rate at which to sample; 0.0 - 100.0. If passed-in zipkin_attrs have is_sampled=False and the sample_rate param is > 0, a new span will be generated at this rate. This means that if you propagate sampling decisions to downstream services, but still have sample_rate > 0 in those services, the actual rate of generated spans for those services will be > sampling_rate. Defaults to 100.
        """
        zipkin_span.__init__(
            self,
            service_name=service_name,
            span_name=span_name,
            transport_handler=OciApmHttpTransport,
            encoding=Encoding.V2_JSON,
            binary_annotations=binary_annotations,
            sample_rate=sample_rate,
        )

    def __enter__(self):
        zipkin_span.__enter__(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        super().__exit__(exc_type, exc_value, exc_traceback)
