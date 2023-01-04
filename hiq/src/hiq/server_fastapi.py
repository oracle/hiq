# HiQ version 1.1.2
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import time

import hiq
from hiq import HiQLatency, HiQMemory
from hiq.constants import *
from hiq.hiq_utils import func_args_handler
from hiq.memory import get_memory_mb

from typing import Union, Callable, List
from hiq.hiq_utils import (
    func_args_handler,
    get_tau_id,
)


class FastAPIReqIdGenerator(object):
    def __call__(self):
        from asgi_correlation_id.context import correlation_id

        return correlation_id.get()


def run_fastapi(app, driver=None, header_name='X-Request-ID', host='0.0.0.0', port=8080, worker=1):
    from asgi_correlation_id import CorrelationIdMiddleware
    from uuid import uuid4
    # from asgi_correlation_id.middleware import is_valid_uuid4

    app.add_middleware(CorrelationIdMiddleware,
                       header_name=header_name,
                       generator=lambda: uuid4().hex,
                       # validator=is_valid_uuid4
                       )

    @app.get("/hiq")
    async def hiq_report():
        from fastapi.responses import HTMLResponse
        if not driver:
            return ""
        r = driver.get_k0s_summary()
        tmp=[]
        for k, span, start, end in r:
            s = f'<tr><td><a href=latency/{k}>🟢 {k}</a><td align=right>{span}<td align=right>{hiq.ts_to_dt(start)}<td align=right>{hiq.ts_to_dt(end)}'
            tmp.append(s)
        resp = '<table width=100%><tr><td width=50% align=left>Req ID<td align=right>Latency<td align=right>Start<td align=right>End' + '\n'.join(tmp) + "</table>"
        html_resp = f"""
                <!DOCTYPE html>
                <html>
                  <head>
                      <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">
                  </head>
                  <body class="bg-white">
                    <section style='font-family: monospace, Times, serif;'>
                        <div class="container mx-auto">
                            <div class="flex flex-col flex-wrap pb-6 mb-2 text-black ">
                                <h1 class="mb-2 text-3xl font-medium text-black">
                                    Request Latency Report
                                </h1>
                                <p class="text-xl leading-relaxed"> HiQ </p> </div> <div class="flex flex-wrap 
                                items-end justify-start w-full transition duration-500 ease-in-out transform bg-white 
                                border-2 border-gray-600 rounded-lg hover:border-white "> <div class="w-full"> <div 
                                class="relative flex flex-col h-full p-8 text-sm"> <pre>{resp}</pre>
                                </div>
                            </div>
                        </div>
                    </section>
                  </body>
                </html>
                """
        return HTMLResponse(content=html_resp, status_code=200)

    @app.get("/latency/{req_id}")
    async def latency(req_id: str):
        if not driver:
            return ""
        from fastapi.responses import HTMLResponse

        t = driver.get_metrics_by_k0(req_id)
        resp = t.get_graph(FORMAT_DATETIME) if t else f"Error: The reqeust id({req_id}) is invalid!"
        html_resp = f"""
        <!DOCTYPE html>
        <html>
          <head>
              <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">
          </head>
          <body class="bg-white">
            <section style='font-family: monospace, Times, serif;'>
                <div class="container mx-auto">
                    <div class="flex flex-col flex-wrap pb-6 mb-2 text-black ">
                        <h1 class="mb-2 text-3xl font-medium text-black">
                            Request Latency Report
                        </h1>
                        <p class="text-xl leading-relaxed">Request Id: {req_id}</p>
                    </div>
                    <div class="flex flex-wrap 
                        items-end justify-start w-full transition duration-500 ease-in-out transform bg-white 
                        border-2 border-gray-600 rounded-lg hover:border-white "> <div class="w-full"> <div 
                        class="relative flex flex-col h-full p-8 text-sm"> <pre>{resp}</pre> </div> </div> <div 
                        class="w-full xl:w-1/4 md:w-1/4 lg:ml-auto"> <div class="relative flex flex-col h-full p-8"> 
                        <button class="w-full px-4 py-2 mx-auto mt-3"> <a href="../hiq">Back to HiQ Report Home 🏠</a> </button> </div> </div> 
                        </div> </section> </body> </html>"""
        return HTMLResponse(content=html_resp, status_code=200)

    import uvicorn
    uvicorn.run(app, host=host, port=port, workers=worker)


def get_corr_id():
    from asgi_correlation_id.context import correlation_id
    return correlation_id.get()


class HiQFastAPILatencyMixin:
    def __init__(sf,
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
        super().__init__(hiq_id_func=hiq_id_func,
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
