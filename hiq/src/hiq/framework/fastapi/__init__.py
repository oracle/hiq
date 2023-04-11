# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#
import os.path
import time

import hiq
from hiq import HiQLatency, HiQMemory
from hiq.constants import *
from hiq.memory import get_memory_mb
from hiq.hiq_utils import func_args_handler

from contextvars import ContextVar
from typing import *
from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional
from uuid import UUID, uuid4

# Middleware
correlation_id: ContextVar[Optional[str]] = ContextVar("correlation_id", default=None)


# if TYPE_CHECKING:
#    from starlette.types import ASGIApp, Message, Receive, Scope, Send


def is_valid_uuid4(uuid_: str) -> bool:
    """
    Check whether a string is a valid v4 uuid.
    """
    try:
        return bool(UUID(uuid_, version=4))
    except ValueError:
        return False


FAILED_VALIDATION_MESSAGE = (
    "Generated new request ID (%s), since request header value failed validation"
)


@dataclass
class CorrelationIdMiddleware:
    app: "ASGIApp"
    header_name: str = "X-Request-ID"

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        """
        Load request ID from headers if present. Generate one otherwise.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def handle_outgoing_request(message: "Message") -> None:
            if message["type"] == "http.response.start" and correlation_id.get():
                from starlette.datastructures import MutableHeaders

                headers = MutableHeaders(scope=message)
                headers.append(self.header_name, correlation_id.get())
                headers.append("Access-Control-Expose-Headers", self.header_name)

            await send(message)

        await self.app(scope, receive, handle_outgoing_request)

    def __post_init__(self) -> None:
        pass


class FastAPIReqIdGenerator(object):
    def __call__(self):
        return correlation_id.get()


g_cpu_info = None
here = os.path.dirname(os.path.realpath(__file__))
g_templates_dir = f"{here}/templates"
fstr_hiq = hiq.read_file(f"{g_templates_dir}/hiq.html", by_line=False)
fstr_lat = hiq.read_file(f"{g_templates_dir}/lat.html", by_line=False)


def run_fastapi(
    driver,
    app,
    header_name="X-Request-ID",
    host="0.0.0.0",
    port=8080,
    worker=1,
    thread_limit=os.cpu_count(),
    endpoints={"/predict"},
    generator=lambda: uuid4().hex,
    custom={"/custom": ("get", None)},
    app_title="Application",
    app_version="1.0.0",
):
    from fastapi import Request

    app.title = app_title
    app.description = "<a href=hiq>HiQ</a>"
    app.version = app_version

    port = int(os.environ.get("HIQ_FLASK_PORT", port))
    worker = int(os.environ.get("HIQ_FLASK_WORKER", worker))

    app.add_middleware(CorrelationIdMiddleware, header_name=header_name)

    @app.middleware("http")
    async def add_latency_header(request: Request, call_next):
        ep = "/" + str(request.url).split("/")[-1]
        if "?" in ep:
            ep = ep.split("?")[0]
        if ep in endpoints or ep in custom.keys():
            cid = (
                request.headers.get(header_name)
                if header_name in request.headers
                else generator()
            )
            correlation_id.set(cid)
            start_time = time.monotonic()
            response = await call_next(request)
            response.headers["X-latency"] = str(time.monotonic() - start_time)
            return response
        else:
            return await call_next(request)

    @app.on_event("startup")
    def startup():
        from anyio.lowlevel import RunVar
        from anyio import CapacityLimiter

        RunVar("_default_thread_limiter").set(CapacityLimiter(thread_limit))

    def not_implemented_func():
        return "NOT_IMPLEMENTED"

    for k, v in custom.items():
        try:
            getattr(app, v[0])(k)(not_implemented_func if v[1] is None else v[1])
        except AttributeError as e:
            print(f"warning: {e}")

    @app.get("/hiq_enable")
    async def hiq_enable():
        if not driver:
            return ""
        driver.enable_hiq()

        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/hiq")

    @app.get("/hiq_disable")
    async def hiq_disable():
        if not driver:
            return ""
        driver.disable_hiq()

        from fastapi.responses import RedirectResponse

        return RedirectResponse(url="/hiq")

    @app.get("/hiq")
    async def hiq_report():
        global g_cpu_info
        from fastapi.responses import HTMLResponse
        import cpuinfo

        if not g_cpu_info:
            cio = cpuinfo.get_cpu_info()
            g_cpu_info = cio["brand_raw"] if "brand_raw" in cio else cio["arch"]
        if not driver:
            return ""
        r = driver.get_k0s_summary()
        tmp = []
        for k, span, start, end in r:
            s = f"<tr><td><a href=latency/{k}>🌲 {k}</a><td align=right>{span}<td align=right>{hiq.ts_to_dt(start)}<td align=right>{hiq.ts_to_dt(end)}"
            tmp.append(s)
        resp = (
            "<table width=100%><tr><td width=50% align=left>Req ID<td align=right>Latency<td align=right>Start<td align=right>End"
            + "\n".join(tmp)
            + "</table>"
        )

        basic_info = f"""
        HiQ: {'🟢 Enabled' if driver.enabled else '🔴 Disabled'},
                                        CPU Type: <span class='highlight'>{g_cpu_info}</span>,
                                        CPU Load: {os.getloadavg()[0]:.2f},
                                        Process Memory: {hiq.memory.get_memory_gb():.2f}GB,
                                        Current System Memory Usage:
                                        <span class='highlight'>
                                            {hiq.get_system_memory_usage()/(1<<30):.2f}GB
                                        </span>,
        """
        if hiq.get_system_peak_memory() > 0:
            basic_info += f"Peak System Memory Usage: <span class='highlight'>{hiq.get_system_peak_memory()/(1<<30):.2f}GB</span>,"
        basic_info += f"Generated at: {hiq.get_time_str_with_tz()}"

        html_resp = fstr_hiq.format(
            hiq_version=hiq.__version__, basic_info=basic_info, latency=resp
        )
        return HTMLResponse(content=html_resp, status_code=200)

    @app.get("/latency/{req_id}")
    async def latency(req_id: str):
        if not driver:
            return ""
        from fastapi.responses import HTMLResponse

        t = driver.get_metrics_by_k0(req_id if req_id != "None" else None)
        resp = (
            t.get_graph(FORMAT_DATETIME)
            if t
            else f"Error: The reqeust id({req_id}) is invalid!"
        )
        html_resp = fstr_lat.format(
            hiq_version=hiq.__version__,
            req_id=req_id if req_id != "None" else "-",
            latency=resp,
        )
        return HTMLResponse(content=html_resp, status_code=200)

    import uvicorn

    uvicorn.run(app, host=host, port=port, workers=worker)


def get_corr_id():
    from asgi_correlation_id.context import correlation_id

    return correlation_id.get()


class HiQFastAPILatencyMixin:
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time],
        hiq_id_func: Callable = FastAPIReqIdGenerator(),
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
        super().__init__(
            hiq_id_func=hiq_id_func,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
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


class HiQFastAPILatency(HiQLatency):
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
            hiq_id_func=FastAPIReqIdGenerator(),
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


class HiQFastAPIMemory(HiQMemory):
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
            hiq_id_func=FastAPIReqIdGenerator(),
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
