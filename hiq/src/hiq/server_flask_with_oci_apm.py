# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import logging
import random
import string

from flask import _app_ctx_stack, current_app, g, request
from py_zipkin import zipkin

from hiq.vendor_oci_apm import OciApmHttpTransport


class FlaskWithOciApm(object):
    """A Flask App's helper class with Oci-Apm supported by default

    To make it work, you need to set two environment variables: APM_BASE_URL, APM_PUB_KEY

    Example:

    .. highlight:: python
    .. code-block:: python

        import os
        import time

        from flask import Flask
        from flask_request_id_header.middleware import RequestID
        from hiq.server_flask_with_oci_apm import FlaskWithOciApm


        def create_app():
            app = Flask(__name__)
            app.config["REQUEST_ID_UNIQUE_VALUE_PREFIX"] = "hiq-"
            RequestID(app)
            return app


        app = create_app()
        amp = FlaskWithOciApm()
        amp.init_app(app)


        @app.route("/", methods=["GET"])
        def index():
            return "OK"


        if __name__ == "__main__":
            host = "0.0.0.0"
            port = int(os.getenv("PORT", "8080"))
            debug = False
            app.run(host=host, port=port, debug=debug)

    """

    def _gen_random_id(self):
        return "".join(random.choice(string.digits) for i in range(16))

    def __init__(
        self,
        app=None,
        sample_rate=100,
        timeout=1,
        transport_handler_=OciApmHttpTransport,
    ):
        self._exempt_views = set()
        self._sample_rate = sample_rate
        if app is not None:
            self.init_app(app)
        self._transport_handler = transport_handler_
        self._transport_exception_handler = None
        self._timeout = timeout

    def init_app(self, app):
        self.app = app
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        self._disable = app.config.get(
            "ZIPKIN_DISABLE", app.config.get("TESTING", False)
        )
        return self

    def _should_use_token(self, view_func):
        return view_func not in self._exempt_views

    def _safe_headers(self, headers):
        self._headers = dict((k.lower(), v) for k, v in headers.__iter__())
        return self._headers

    def _before_request(self):
        if self._disable:
            return

        _app_ctx_stack.top._view_func = current_app.view_functions.get(request.endpoint)

        if not self._should_use_token(_app_ctx_stack.top._view_func):
            return

        safe_headers = self._safe_headers(request.headers)

        parent_span_id = safe_headers.get("x-b3-parentspanid")
        trace_id = safe_headers.get("x-b3-traceid") or self._gen_random_id()
        is_sampled = str(safe_headers.get("x-b3-sampled") or "0") == "1"

        flags = safe_headers.get("x-b3-flags")

        zipkin_attrs = zipkin.ZipkinAttrs(
            trace_id=trace_id,
            span_id=self._gen_random_id(),
            parent_span_id=parent_span_id,
            flags=flags,
            is_sampled=is_sampled,
        )

        span = zipkin.zipkin_span(
            service_name=self.app.name,
            span_name="{0}.{1}".format(request.endpoint, request.method),
            transport_handler=self._transport_handler,
            sample_rate=self._sample_rate,
            zipkin_attrs=zipkin_attrs,
        )
        g._zipkin_span = span
        g._zipkin_span.start()

    def exempt(self, view):
        view_location = "{0}.{1}".format(view.__module__, view.__name__)
        self._exempt_views.add(view_location)
        return view

    def _after_request(self, response):
        if self._disable:
            return response
        if not hasattr(g, "_zipkin_span"):
            return response
        try:
            g._zipkin_span.stop()
        except Exception as e:
            logging.warning("Unable to stop zipkin span:{}".format(e))

        return response

    def create_http_headers_for_new_span(self):
        if self._disable:
            return dict()
        return zipkin.create_http_headers_for_new_span()

    def logging(self, **kwargs):
        logging.warning(
            "This method has been deprecated, " "please call `update_tags` instead."
        )
        self.update_tags(**kwargs)

    def update_tags(self, **kwargs):
        if all(
            [hasattr(g, "_zipkin_span"), g._zipkin_span, g._zipkin_span.logging_context]
        ):
            g._zipkin_span.logging_context.binary_annotations_dict.update(kwargs)


def child_span(f):
    def decorated(*args, **kwargs):
        import flask

        span = zipkin.zipkin_span(
            service_name=flask.current_app.name,
            span_name=f.__name__,
        )
        kwargs["span"] = span
        with span:
            val = f(*args, **kwargs)
            span.update_binary_annotations(
                {
                    "function_args": args,
                    "function_returns": val,
                }
            )
            return val

    return decorated
