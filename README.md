# HiQ - A Declarative, Non-intrusive, Dynamic, and Transparent Tracking and Optimization System

HiQ is here to blow your mind by introducing a `declarative`, `non-intrusive`, `dynamic` and `transparent` tracking and optimization system for both **monolithic** application and **distributed** system. It brings the runtime information tracking and optimization to a new level which you can never imagine before. Yet, HiQ doesn't compromise with speed and system performance, or hide any tracking overhead information. HiQ applies for both I/O bound and CPU bound applications. Especially for CPU bound application, HiQ is by far the **one and only one perfect solution in the industry**.

To explain the four features, **declarative** means you can declare the things you want to track in a text file, which could be a json, yaml or even csv,and no need to change program code. **Non-intrusive** means HiQ doesn't requires to modify original code. **Dynamic** means HiQ supports software metrics featuring at run time, which can be used for adaptive tracing. **Transparent** means HiQ provides the tracing overhead and doesn't hide it no matter it is huge or tiny.

In addition to latency tracking, HiQ provides memory, disk I/O and Network I/O tracking out of the box. The output can be saved in form of normal line by line log file, or HiQ tree, or span graph. For long running server application, HiQ helps to automatically optimize your program and make it more robust using machine learning technology.

## Environment

- Python 3.6+
- Linux, MacOS

## Installation

### Method 1 - build from source

git clone this repo and cd into the source code, and run:

```python
python setup.py bdist_wheel && \
pip install --force-reinstall dist/hiq-1.0.0-*.whl
```

### Method 2 - install with pip if you are in Oracle corp network

```bash
pip install --force-reinstall python-hiq
```



## Quick Start

Let start with a simplest example by running HiQ against a monolithic application called `target_code.py`. Run the following code:

```python
cd docs
python run_agent.py
```

If everything is fine, you should be able to see four hiq trees printed out.

![Run A Simplest Example](run_agent.jpg)

### Explanation

You have a python code `target_code.py` and you want to find the run-time latency, memory, disk I/O, network I/O information of each functions without modifying its code and without compromise on performance. HiQ is here to help you.

Let's go through the code line by line and learn how HiQ help to solve the problem:

```python
  1 import os
  2 import hiq
  3 import traceback, sys
  4 from hiq.hiq_utils import get_global_hiq_status, set_global_hiq_status
  5 from unittest.mock import MagicMock
  6
  7 here = os.path.dirname(os.path.realpath(__file__))
  8
  9
 10 def run_target_code():
 11     _g_tau_original = get_global_hiq_status()
 12     set_global_hiq_status(True)
 13     tau = hiq.HiQLatency(
 14         hiq_table_or_path=f"{here}/target_code.conf",
 15         max_hiq_size=4,
 16     ).enable_hiq()
 17
 18     for i in range(4):
 19         tau.get_tau_id = MagicMock(return_value=i)
 20         try:
 21             hiq.mod("target_code").fit(data={}, model=[i])
 22         except Exception as e:
 23             traceback.print_exc(file=sys.stdout)
 24     tau.show()
 25
 26     tau.disable_hiq()
 27     print("-^" * 20, "disable HiQ", "-^" * 20)
 28     hiq.mod("target_code").fit(data={}, model=[i])
 29     set_global_hiq_status(_g_tau_original)
 30
 31
 32 if __name__ == "__main__":
 33     run_target_code()
```

From line 1 to 5: import necessary modules and functions. `get_global_hiq_status` and `set_global_hiq_status` are used to get and set the global hiq status. If the status is on, HiQ will function; if off, HiQ will stop working but you can still run the program.

Line 7: get the current directory path.

Line 10: define a function called `run_target_code`.

Line 11 to 12: back up the original HiQ status and set it to True

Line 13 to 16: create an object `tau` which has a type of class `hiq.HiQLatency`. `hiq.HiQLatency` is for latency tracking. We have `hiq.HiQMemory` to track both latency and memory. Users can also inherit `hiq.HiQSimple` to customize the metrics they want to track, but that is an advanced topics. But for now, in this case, we just need `hiq.HiQLatency` to track latency.

Line 18 to 23: run the target_code 4 times.

Line 24: print the performance metrics as a tree.

Line 26: disable HiQ

Line 28: run the target_code once again.

Line 29: set the global hiq status back to what it was before this run

## Integration with Oracle APM

HiQ integrates with OCI APM by class `hiq.vendor.OciApmHttpTransport`.

### Quick Start

```python
  1 import time
  2
  3 from py_zipkin import Encoding
  4 from py_zipkin.zipkin import zipkin_span
  5 from hiq.vendor_oci_apm import OciApmHttpTransport
  6
  7
  8 def fun():
  9     with zipkin_span(
 10         service_name="hiq_test_apm",
 11         span_name="fun_test",
 12         transport_handler=OciApmHttpTransport,
 13         encoding=Encoding.V2_JSON,
 14         binary_annotations={"mode": "sync"},
 15         sample_rate=100,
 16     ):
 17         time.sleep(5)
 18         print("hello")
 19
 20
 21 if __name__ == "__main__":
 22     fun()
```

Run this code you can see the result in APM trace explorer.

![HiQ integration with OCI APM](oci_apm_1.jpg)

### Non-intrusive Integration with Flask and OCI APM

HiQ can integrate with Flask and OCI APM by class `FlaskWithOciApm`. This can be used in distributed tracing.

```python
  1 import os
  2 import time
  3 
  4 from flask import Flask
  5 from flask_request_id_header.middleware import RequestID
  6 from hiq.server_flask_with_oci_apm import FlaskWithOciApm
  7 
  8 
  9 def create_app():
 10     app = Flask(__name__)
 11     app.config["REQUEST_ID_UNIQUE_VALUE_PREFIX"] = "hiq-"
 12     RequestID(app)
 13     return app
 14 
 15 
 16 app = create_app()
 17 
 18 amp = FlaskWithOciApm()
 19 amp.init_app(app)
 20 
 21 
 22 @app.route("/", methods=["GET"])
 23 def index():
 24     time.sleep(2)
 25     return "OK"
 26 
 27 
 28 @app.route("/predict", methods=["GET"])
 29 def predict():
 30     time.sleep(1)
 31     return "OK"
 32 
 33 
 34 if __name__ == "__main__":
 35     host = "0.0.0.0"
 36     port = int(os.getenv("PORT", "8080"))
 37     debug = False
 38     app.run(host=host, port=port, debug=debug)
```

All the endpoints requests information will be recorded  and available for analysis in APM.

![](server_flask_apm.jpg)

---

For more advanced topics like `Log MonkeyKing`, `LumberJack`, `HiQ Distributed Tracing`, and `HiQ Service Mesh and K8S integration`, `HiQ vs cProfile/ZipKin/Jaeger/Skywalking`, please refer to the [official document](#).
