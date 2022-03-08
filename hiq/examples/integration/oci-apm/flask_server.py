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
    time.sleep(2)
    return "OK"


@app.route("/predict", methods=["GET"])
def predict():
    time.sleep(1)
    return "OK"


if __name__ == "__main__":
    host = "0.0.0.0"
    port = int(os.getenv("PORT", "8080"))
    debug = False
    app.run(host=host, port=port, debug=debug)
