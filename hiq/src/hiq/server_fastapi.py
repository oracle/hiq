# HiQ version 1.0.
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


def run_fastapi(app, driver=None, header_name='X-Request-ID'):
    from asgi_correlation_id import CorrelationIdMiddleware
    from uuid import uuid4
    # from asgi_correlation_id.middleware import is_valid_uuid4

    app.add_middleware(CorrelationIdMiddleware,
                       header_name=header_name,
                       generator=lambda: uuid4().hex,
                       # validator=is_valid_uuid4
                       )

    @app.get("/latency/{req_id}")
    async def latency(req_id: str):
        if not driver:
            return ""
        from fastapi.responses import HTMLResponse

        t = driver.get_metrics_by_k0(req_id)
        resp = t.get_graph().replace('\n', '<br>').replace(' ', '&nbsp') if t else f"Error: The reqeust id({req_id}) " \
                                                                                   f"is invalid!"
        html_resp = f"""
        <!DOCTYPE html>
        <html>
          <head>
              <link href="https://unpkg.com/tailwindcss@^2/dist/tailwind.min.css" rel="stylesheet">
          </head>
          <body class="bg-black">
            <section style='font-family: monospace, Times, serif;'>
                <div class="container px-5 py-12 mx-auto lg:px-20">
                    <div class="flex flex-col flex-wrap pb-6 mb-12 text-white ">
                        <h1 class="mb-12 text-3xl font-medium text-white">
                            Request Latency Report
                        </h1>
                        <p class="text-xl leading-relaxed">Request Id: {req_id}</p> </div> <div class="flex flex-wrap 
                        items-end justify-start w-full transition duration-500 ease-in-out transform bg-black 
                        border-2 border-gray-600 rounded-lg hover:border-white "> <div class="w-full"> <div 
                        class="relative flex flex-col h-full p-8 "> <p class="flex items-center mb-2 text-lg 
                        font-normal tracking-wide text-white"> {resp}
                            </p>
                        </div>
                    </div>
                </div>
            </section>
          </body>
        </html>
        """
        return HTMLResponse(content=html_resp, status_code=200)

    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


def get_corr_id():
    from asgi_correlation_id.context import correlation_id
    return correlation_id.get()


class HiQFastAPILatencyMixin:
    def __init__(sf):
        super().__init__(hiq_id_func=FastAPIReqIdGenerator())


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
