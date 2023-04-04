# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import time

import hiq
from hiq import HiQLatency, HiQMemory
from hiq.constants import *
from hiq.hiq_utils import FlaskReqIdGenerator, func_args_handler
from hiq.memory import get_memory_mb

from typing import Union, Callable, List
from hiq.hiq_utils import (
    func_args_handler,
    get_tau_id,
)


class HiQFlaskLatency(HiQLatency):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time],
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        HiQLatency.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=FlaskReqIdGenerator(),
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )

    def custom(sf):
        pass

    def custom_disable(sf):
        pass


class HiQFlaskMemory(HiQMemory):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time, get_memory_mb],
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        HiQLatency.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=FlaskReqIdGenerator(),
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )

    def custom(sf):
        pass

    def custom_disable(sf):
        pass


class HiQFlaskLatencyOtel(hiq.HiQSimple):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
        trace=None,
        trace_provider=None,
        tracer_name=None,
        span_processor=None,
        exporter=None,
        endpoints=None,
    ):
        """In addition to arguments of normal HiQLatency, there are several new arguments for OpenTelemetry:
        trace, trace_provider, tracer_name, span_processor, exporter, endpoints

        endpoints - server endpoints on which metrics will be sent
        """
        hiq.HiQSimple.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=hiq_id_func,
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )
        sf.trace = trace or hiq.mod("opentelemetry.trace")
        sf.trace.set_tracer_provider(
            trace_provider or hiq.mod("opentelemetry.sdk.trace").TracerProvider()
        )
        sf.tracer = sf.trace.get_tracer_provider().get_tracer(tracer_name or __name__)
        sf.exporter = (
            exporter or hiq.mod("opentelemetry.sdk.trace.export").ConsoleSpanExporter()
        )
        sf.span_processor = span_processor or hiq.mod(
            "opentelemetry.sdk.trace.export"
        ).BatchSpanProcessor(sf.exporter)

        sf.trace.get_tracer_provider().add_span_processor(sf.span_processor)
        sf.endpoints = endpoints

    def custom(s):
        s.o_flask_dispatch_request = hiq.mod("flask").Flask.dispatch_request

        def flask_dispatch_request(self):
            from flask import request
            from opentelemetry.instrumentation.wsgi import collect_request_attributes
            from opentelemetry.propagate import extract

            if s.endpoints is None or str(request.endpoint) not in s.endpoints:
                return s.o_flask_dispatch_request(self)

            req_env = collect_request_attributes(request.environ)
            with s.tracer.start_as_current_span(
                str(request.endpoint),
                context=extract(request.headers),
                kind=s.trace.SpanKind.SERVER,
                attributes=req_env,
            ):
                # print(req_env)
                return s.o_flask_dispatch_request(self)

        hiq.mod("flask").Flask.dispatch_request = flask_dispatch_request

    def custom_disable(s):
        hiq.mod("flask").Flask.dispatch_request = s.o_flask_dispatch_request
