# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

from enum import Enum
import os
from typing import Optional, Sequence
import itree
from hiq.hiq_utils import TRACING_TYPE_OTM
from hiq.utils import memoize_first


class OtmExporterType(Enum):
    JAEGER_THRIFT = 1
    JAEGER_PROTOBUF = 2
    ZIPKIN_JSON = 3
    ZIPKIN_PROTOBUF = 4


def setup_jaeger(
    service_name="hiq_service",
    agent_host_name="localhost",
    agent_port=6831,
    tracer_name="otm_hiq",
    collector_endpoint="localhost:14250",
    exporter_type: OtmExporterType = OtmExporterType.JAEGER_THRIFT,
):
    """Set up jaeger client

    Args:
        service_name (str, optional): the name of the service. Defaults to "hiq_service".
        agent_host_name (str, optional): jaeger agent host name. Defaults to "localhost".
        agent_port (int, optional): jaeger agent port. Defaults to 6831.
        tracer_name (str, optional): tracer name. Defaults to "otm_hiq".
    """

    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    )
    if exporter_type == OtmExporterType.JAEGER_THRIFT:
        jaeger_exporter = itree.mod(
            "opentelemetry.exporter.jaeger.thrift"
        ).JaegerExporter(
            agent_host_name=agent_host_name,
            agent_port=agent_port,
        )
    elif exporter_type == OtmExporterType.JAEGER_PROTOBUF:
        jaeger_exporter = itree.mod(
            "opentelemetry.exporter.jaeger.proto.grpc"
        ).JaegerExporter(collector_endpoint=collector_endpoint, insecure=True)
    else:
        raise ValueError(f"wrong exporter type: {exporter_type}")

    trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

    os.environ["OTM_TRACER_NAME"] = tracer_name


def setup_zipkin(
    service_name="hiq_service",
    tracer_name="otm_hiq",
    endpoint: Optional[str] = "http://localhost:9411/api/v2/spans",
    local_node_ipv4=None,
    local_node_port: Optional[int] = None,
    max_tag_value_length: Optional[int] = 256,
    timeout: Optional[int] = 5,
    exporter_type: OtmExporterType = OtmExporterType.ZIPKIN_JSON,
):
    from opentelemetry import trace
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.exporter.zipkin.encoder import Protocol
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    trace.set_tracer_provider(
        TracerProvider(resource=Resource.create({SERVICE_NAME: service_name}))
    )

    if exporter_type == OtmExporterType.ZIPKIN_JSON:
        zipkin_exporter = itree.mod(
            "opentelemetry.exporter.zipkin.json"
        ).ZipkinExporter(
            version=Protocol.V2,
            endpoint=endpoint,
            local_node_ipv4=local_node_ipv4,
            local_node_port=local_node_port,
            max_tag_value_length=max_tag_value_length,
            timeout=timeout,  # (in seconds)
        )
    elif exporter_type == OtmExporterType.ZIPKIN_PROTOBUF:
        zipkin_exporter = itree.mod(
            "opentelemetry.exporter.zipkin.proto.http"
        ).ZipkinExporter(
            endpoint=endpoint,
            local_node_ipv4=local_node_ipv4,
            local_node_port=local_node_port,
            max_tag_value_length=max_tag_value_length,
            timeout=timeout,  # (in seconds)
        )
    else:
        raise ValueError(f"wrong exporter type: {exporter_type}")

    # Create a BatchSpanProcessor and add the exporter to it
    span_processor = BatchSpanProcessor(zipkin_exporter)

    # add to the tracer
    trace.get_tracer_provider().add_span_processor(span_processor)
    os.environ["OTM_TRACER_NAME"] = tracer_name


class HiQOpenTelemetryContext(object):
    """OpenTelemetry Context Manager with HiQ

    Example:

    .. highlight:: python
    .. code-block:: python

        import os

        import hiq
        from hiq.distributed import HiQOpenTelemetryContext, OtmExporterType

        here = os.path.dirname(os.path.realpath(__file__))


        def run_main():
            with HiQOpenTelemetryContext(
                exporter_type=OtmExporterType.JAEGER_PROTOBUF,
                collector_endpoint="localhost:14250"
            ):
                driver = hiq.HiQLatency(f"{here}/hiq.conf")
                hiq.mod("main").main()
                driver.show()


        if __name__ == "__main__":
            run_main()
    """

    from opentelemetry import trace

    o_get_tracer = trace.get_tracer

    @staticmethod
    @memoize_first
    def get_tracer_by_name(name):
        return HiQOpenTelemetryContext.o_get_tracer(name)

    def __init__(
        self,
        exporter_type: OtmExporterType = OtmExporterType.JAEGER_THRIFT,
        *args,
        **kwargs,
    ):
        self.exporter_type = exporter_type
        if self.exporter_type in [
            OtmExporterType.JAEGER_THRIFT,
            OtmExporterType.JAEGER_PROTOBUF,
        ]:
            kwargs["exporter_type"] = self.exporter_type
            setup_jaeger(*args, **kwargs)
        elif self.exporter_type in [
            OtmExporterType.ZIPKIN_JSON,
            OtmExporterType.ZIPKIN_PROTOBUF,
        ]:
            kwargs["exporter_type"] = self.exporter_type
            setup_zipkin(*args, **kwargs)
        else:
            raise ValueError("Unknown exporter type")

    def __enter__(self):
        """To enable OpenTelemetry support, you need to set environment variable TRACE_TYPE equal to opentelemetry."""
        os.environ["TRACE_TYPE"] = TRACING_TYPE_OTM
        self.old_get_tracer = HiQOpenTelemetryContext.trace.get_tracer
        HiQOpenTelemetryContext.trace.get_tracer = (
            HiQOpenTelemetryContext.get_tracer_by_name
        )
        tracer_name = os.environ.get("OTM_TRACER_NAME", "otm_hiq")
        HiQOpenTelemetryContext.trace.get_tracer(tracer_name)

    def __exit__(self, exc_type, exc_value, exc_tb):
        HiQOpenTelemetryContext.trace.get_tracer = self.old_get_tracer
        del os.environ["TRACE_TYPE"]
