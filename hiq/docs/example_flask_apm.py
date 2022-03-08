import os
import time

from hiq.server_flask_with_oci_apm import FlaskWithOciApm


def create_app():
    from flask import Flask
    from flask_request_id_header.middleware import RequestID

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


"""
    HHHHHHHHH     HHHHHHHHH  iiii       QQQQQQQQQ      
    H:::::::H     H:::::::H i::::i    QQ:::::::::QQ    
    H:::::::H     H:::::::H  iiii   QQ:::::::::::::QQ  
    HH::::::H     H::::::HH        Q:::::::QQQ:::::::Q 
      H:::::H     H:::::H  iiiiiii Q::::::O   Q::::::Q 
      H:::::H     H:::::H  i:::::i Q:::::O     Q:::::Q 
      H::::::HHHHH::::::H   i::::i Q:::::O     Q:::::Q 
      H:::::::::::::::::H   i::::i Q:::::O     Q:::::Q 
      H:::::::::::::::::H   i::::i Q:::::O     Q:::::Q 
      H::::::HHHHH::::::H   i::::i Q:::::O     Q:::::Q 
      H:::::H     H:::::H   i::::i Q:::::O  QQQQ:::::Q 
      H:::::H     H:::::H   i::::i Q::::::O Q::::::::Q 
    HH::::::H     H::::::HHi::::::iQ:::::::QQ::::::::Q 
    H:::::::H     H:::::::Hi::::::i QQ::::::::::::::Q  
    H:::::::H     H:::::::Hi::::::i   QQ:::::::::::Q   
    HHHHHHHHH     HHHHHHHHHiiiiiiii     QQQQQQQQ::::QQ 
                                                Q:::::Q
                                                 QQQQQQ


"""
