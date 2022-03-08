import io
import json
import logging
import os

import hiq
from hiq.distributed import HiQOpenTelemetryContext, OtmExporterType
from fdk import response

here = os.path.dirname(os.path.realpath(__file__))


def run_main():
    with HiQOpenTelemetryContext(exporter_type=OtmExporterType.ZIPKIN_JSON):
        _ = hiq.HiQLatency(f"{here}/hiq.conf")
        hiq.mod("main").main()


def handler(ctx, data: io.BytesIO = None):
    name = "World"
    try:
        run_main()
        body = json.loads(data.getvalue())
        name = body.get("name")
    except (Exception, ValueError) as ex:
        logging.getLogger().info("error parsing json payload: " + str(ex))

    logging.getLogger().info("Inside Python Hello World function")
    return response.Response(
        ctx,
        response_data=json.dumps({"message": "Hello {0}".format(name)}),
        headers={"Content-Type": "application/json"},
    )
