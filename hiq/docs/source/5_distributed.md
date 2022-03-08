# HiQ Distributed Tracing


Distributed tracing is the capability for a tracing solution to track and observe service requests as they flow through distributed systems by collecting data as the requests go from one service to another. The trace data helps you understand the flow of requests through your microservices environment and pinpoint where failures or performance issues are occurring in the system—and why.


## OpenTelemetry

```eval_rst
.. thumbnail:: img/OpenTelemetry.png
    :width: 220px
    :height: 100px
```

OpenTelemetry is a set of APIs, SDKs, tooling and integrations that are designed for the creation and management of telemetry data such as traces, metrics, and logs. It is vendor neutral, so It doesn't specify implementation details like Jaeger or Zipkin. OpenTelemetry provides default implementations for all the tracing backends and vendors, while allowing users to choose a different implementation for vendor specific features.


```eval_rst
.. thumbnail:: img/otel.jpg
    :width: 800px
    :height: 250px
```

**HiQ supports OpenTelemetry out of the box** by context manager `HiQOpenTelemetryContext`.

To get OpenTelemetry and the code examples in this chapter working, install both the opentelemetry API and SDK:

```
pip install opentelemetry-api
pip install opentelemetry-sdk
```

The API package provides the interfaces required by the application owner, as well as some helper logic to load implementations. The SDK provides an implementation of those interfaces. The implementation is designed to be generic and extensible enough that in many situations, the SDK is sufficient. You won't use them directly but it is needed by HiQ.

## Jaeger

```eval_rst
.. thumbnail:: img/jaeger-logo.png
    :width: 300px
    :height: 100px
```

Jaeger, inspired by Dapper and OpenZipkin, is a distributed tracing platform created by Uber Technologies and donated to Cloud Native Computing Foundation. It can be used for monitoring microservices-based distributed systems:

- Distributed context propagation  
- Distributed transaction monitoring  
- Root cause analysis  
- Service dependency analysis  
- Performance / latency optimization

https://www.jaegertracing.io/

**HiQ supports Jaeger out of the box** too.

### Set Up

The following is an example which assume you have jager server/agent running locally. If you don't have, you can run the command to start a docker instance for jager server:


```bash
docker run --rm --name hiq_jaeger \
  -e COLLECTOR_ZIPKIN_HOST_PORT=:9411 \
  -p 5775:5775/udp \
  -p 6831:6831/udp \
  -p 6832:6832/udp \
  -p 5778:5778 \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 14250:14250 \
  -p 9411:9411 \
  jaegertracing/all-in-one
```

The target code is the same as before:

```eval_rst
.. literalinclude:: ../../examples/distributed/jaeger/main.py
   :language: python
   :linenos:
```

Jeager supports two protocols: `thrift` and `protobuf`.

### Thrift + HiQ

Below is the driver code for `thrift`. You can see the only change is line 4 and 10. You only need to add a context manager `hiq.distributed.HiQOpenTelemetryContext` to get the jaeger tracing working.

```eval_rst
.. literalinclude:: ../../examples/distributed/jaeger/main_driver_thrift.py
   :language: python
   :emphasize-lines: 4, 10
   :linenos:
```

Run the driver code and check Jaeger UI at `http://localhost:16686`, you can see the traces have been recorded:

```eval_rst
.. thumbnail:: img/jaeger_th.jpg
```

### Protobuf + HiQ

`Protobuf` works the same way. You just need to replace `OtmExporterType.JAEGER_THRIFT` with `OtmExporterType.JAEGER_PROTOBUF`. This exporter always sends traces to the configured agent using Protobuf via gRPC.

```eval_rst
.. literalinclude:: ../../examples/distributed/jaeger/main_driver_protobuf.py
   :language: python
   :emphasize-lines: 2
   :pyobject: run_main
   :linenos:
```

Run the driver code, and refresh Jaeger UI. We can see a new trace appears in Jaeger UI:

```eval_rst
.. thumbnail:: img/jaeger_pb.jpg

Click the new trace and we can see:

.. thumbnail:: img/jaeger_pb2.jpg
```



## ZipKin


HiQ allows exporting of OpenTelemetry traces to Zipkin. This sends traces to the configured Zipkin collector endpoint using:

- JSON over HTTP with support of multiple versions (v1, v2)  
- HTTP with support of v2 protobuf

### Set Up

The quickest way to start a Zipkin server is to fetch the latest released server as a self-contained executable jar. Note that the Zipkin server requires minimum JRE 8. For example:

```bash
$ curl -sSL https://zipkin.io/quickstart.sh | bash -s
$ java -jar zipkin.jar
```

If everything is fine, you should see a Zipkin logo like:


```eval_rst
.. thumbnail:: img/zipkin_server.jpg
```

```eval_rst
.. note::

   You can use the Jaeger server (port `9411`) we launched too. But according to my test, it only works for JSON + HTTP mode, not Protobuf mode. However, the official Zipkin server works for both modes. Get the latest version at: https://github.com/openzipkin/zipkin.
```

The target code is the same as before.

### JSON + HTTP + HiQ

```eval_rst
.. literalinclude:: ../../examples/distributed/zipkin/main_driver_json.py
   :language: python
   :emphasize-lines: 4, 10
   :linenos:
```

Run the driver code and check the Zipkin web UI.

```eval_rst
.. thumbnail:: img/zipkin_pb_1.jpg
```

Click the `SHOW` button and we can see:

```eval_rst
.. thumbnail:: img/zipkin_pb_2.jpg
```


The default endpoint is `http://localhost:9411/api/v2/spans`. If there is a different endpoint `xxx`, you should add `endpoint='xxx'` as one of `HiQOpenTelemetryContext`'s arguments in the constructor.

### Protobuf + HiQ

```eval_rst
.. literalinclude:: ../../examples/distributed/zipkin/main_driver_protobuf.py
   :language: python
   :emphasize-lines: 4, 10
   :linenos:
```

Run the driver code and check the Zipkin web UI. We can see a new trace has been recorded.

```eval_rst
.. thumbnail:: img/zipkin_3.jpg
```


## Ray

- Installation

```
pip install ray
```

## Dask

```
pip install dask
```
