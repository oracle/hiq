
# HiQ Vendor Integration

## OCI APM

[OCI Application Performance Monitoring (APM)](https://www.oracle.com/manageability/application-performance-monitoring/) is a service that provides deep visibility into the performance of applications and enables DevOps professionals to diagnose issues quickly in order to deliver a consistent level of service.

**HiQ supports OCI APM out of the box.**

### Get APM Endpoint and Environments Setup

To use Oracle APM, we need to have the APM server's endpoint. To get the endpoint, you should copy your own `APM_BASE_URL` and `APM_PUB_KEY` from OCI web console and set them as environment variables.


```eval_rst
.. thumbnail:: img/apm-setup.jpg
   :width: 800px
   :height: 600px
   :title: (A screenshot of a typical APM Domains UI)
   :show_caption: True

```

`APM_BASE_URL` is the `Data Upload Endpoint` in `APM Domains` page; `APM_PUB_KEY` is the **public** key named `auto_generated_public_datakey` in the same page. You can just click the word `show` to copy them.


```eval_rst
  .. warning::
     The values below are fake and for demo purposes only. You should replace them with your own `APM_BASE_URL` and `APM_PUB_KEY`.
```

Then you can set them in the terminal like:

```bash
export APM_BASE_URL="https://aaaac64xyvkaiaaaxxxxxxxxxx.apm-agt.us-phoenix-1.oci.oraclecloud.com"
export APM_PUB_KEY="JL6DVW2YBYYPA6G53UG3ZNAJSHSBSHSN"
```

```eval_rst
  .. tip::
  
      "The public key and public channel supposed to be used by something like a browser in which any end user may see the key. For server side instrumentation you should use the private data key. Changing this will make no difference in any way. The idea is that you may want/need to change the public key more often."

      --Avi Huber
```

You can also set it in your python code programmatically with `os.environ` like what we have done in previous chapter.

----

There are two ways to use OCI APM in HiQ. The legacy way is to use `HiQOciApmContext` which uses `py_zipkin` under the hood. The modern way is to use `HiQOpenTelemetryContext`, which uses the new `OpenTelemetry` api.

### HiQOciApmContext

The first way to send data to OCI APM is to use `HiQOciApmContext`. To use `HiQOciApmContext`, you need to install `py_zipkin`:

```bash
pip install py_zipkin
```

#### A Quick Start Demo

With the two environment variables set, we can write the following code:

```eval_rst
.. literalinclude:: ../../examples/integration/oci-apm/quick_start.py
   :language: python
   :emphasize-lines: 8-10, 16
   :linenos:
```

Run this code you can see the result in APM trace explorer.

```eval_rst
.. thumbnail:: img/oci_apm_1.jpg
```



#### Monolithic Application Performance Monitoring

Just like before, we have the same target code.

```eval_rst
.. literalinclude:: ../../examples/integration/oci-apm/main.py
   :language: python
   :linenos:
```


This is the driver code:

```eval_rst
.. literalinclude:: ../../examples/integration/oci-apm/main_driver.py
   :language: python
   :emphasize-lines: 4, 10-12, 18
   :linenos:
```

To view the performance in Oracle APM with HiQ, you just need to:

- Set environment variable `TRACE_TYPE` equal to `oci-apm` (Line 18)
- Create a `HiQOciApmContext` object using `with` clause and put everything under its scope (Line 10-12)


Run this code and check APM trace explorer in the web console.

```eval_rst
.. thumbnail:: img/mon-apm.jpg
```

We got a 4-span trace! Click `hiq_doc: main_driver` and we can see `Trace Details` page:

```eval_rst
.. thumbnail:: img/apm-trace-details.jpg
```

#### HiQ with Flask and OCI APM

HiQ can integrate with Flask and OCI APM by class `FlaskWithOciApm` in a non-intrusive way. This can be used in distributed tracing.



```eval_rst
.. literalinclude:: ../../examples/integration/oci-apm/flask_server.py
   :language: python
   :emphasize-lines: 6, 18
   :linenos:
```

All the endpoints requests information will be recorded  and available for analysis in APM.

```eval_rst
.. thumbnail:: img/server_flask_apm.jpg
```

### HiQOpenTelemetryContext

The second way to send data to OCI APM is to use `HiQOpenTelemetryContext`, which leverage OpenTelemetry api under the hood.


For the same target code, the driver code is like:

```eval_rst
.. literalinclude:: ../../examples/integration/oci-apm/main_driver_otel.py
   :language: python
   :emphasize-lines: 4, 10
   :linenos:
```


```eval_rst
  .. note::
     OCI APM doesn't support Protobuf metrics data for now. Only Json format data via HTTP is supported. So `OtmExporterType.ZIPKIN_JSON` is required in line 10 above.
```

Run the driver code and go to the OCI APM web console, we can see:

```eval_rst
.. thumbnail:: img/oci_apm_otel1.jpg
```

Click `hiq_service: __main`, we can see the trace details:

```eval_rst
.. thumbnail:: img/oci_apm_otel2.jpg
```

### Reference

- [OCI Application Performance Monitoring](https://docs.oracle.com/en-us/iaas/application-performance-monitoring/index.html)


## OCI Functions

First you need to add `hiq` in the `requirements.txt`:

```eval_rst
.. literalinclude:: ../../examples/integration/oci-func/requirements.txt
   :language: python
   :emphasize-lines: 2
   :linenos:
```

We can easily send metrics data to APM inside an OCI function like below:

```eval_rst
.. literalinclude:: ../../examples/integration/oci-func/func.py
   :language: python
   :emphasize-lines: 7, 13-16, 22
   :linenos:
```

OCI Function is normally memory constrained. So you can use `HiQMemory` to replace `HiQLatency` above to get the memory consumption details.


## OCI Telemetry(T2) [Internal]

The Oracle Telemetry (T2) system provides REST APIs to help with gathering metrics, creating alarms, and sending notifications to monitor services built on the OCI platform. HiQ integrates with T2 seamlessly.


```eval_rst
 .. autoclass:: hiq.vendor_oci_t2.OciT2Client

    .. automethod:: __init__

    .. automethod:: timing_metric_data

    .. automethod:: wrap_metric_data

    .. automethod:: submit_metrics_queue

    .. automethod:: gauge_metric

    .. automethod:: timing_metric

    .. automethod:: get

```

## OCI Streaming

[The OCI(Oracle Cloud Infrastructure) Streaming service](https://docs.oracle.com/en-us/iaas/Content/Streaming/home.htm) provides a fully managed, scalable, and durable solution for ingesting and consuming high-volume data streams in real-time. Streaming is compatible with most Kafka APIs, allowing you to use applications written for Kafka to send messages to and receive messages from the Streaming service without having to rewrite your code. HiQ integrates with OCI streaming seamlessly.

To use OCI streaming you need to install oci python package first:

```bash
pip install oci
```

Then set up OCI streaming service and create a stream called `hiq` for instance. Please refer to [OCI Streaming Document](https://docs.oracle.com/en-us/iaas/Content/Streaming/Tasks/managingstreams.htm) for how to set them up.

The target code is the same as before, and the following is the sample driver code:

```eval_rst
.. literalinclude:: ../../examples/jack/oci-streaming/main_driver.py
   :language: python
   :emphasize-lines: 20-27
   :linenos:
```

Due to the high latency of Kafka message sending, we process the metrics in the unit of HiQ tree in another process `Jack`. What you need to do is to set the environment variables `JACK` and `HIQ_OCI_STREAMING` to `1` like line 20 and 21, and also the streaming endpoint(`OCI_STM_END`) and streaming OCID(`OCI_STM_OCID`) with the information from your OCI web console.

Run the driver code and then go to OCI web console, you can see the HiQ trees have been recorded.

```eval_rst
.. thumbnail:: img/hiq_oci_streaming.jpg
   :title: (HiQ integration with OCI Steaming)
   :show_caption: True

```

## Prometheus

[Prometheus](https://prometheus.io/) is an open-source systems **monitoring** and **alerting** toolkit originally built at SoundCloud, now a CNCF (Cloud Native Computing Foundation) project used by many companies and organizations. Prometheus collects and stores its metrics as time series data, i.e. metrics information is stored with the timestamp at which it was recorded, alongside optional key-value pairs called labels. If the targe code/service is a long running service, Prometheus is a good option for monitoring solution. **HiQ provide an out-of-the-box solution for Prometheus.**

Like the other integration methods, you need to set environment variable `TRACE_TYPE`. To enable prometheus monitoring, you need to set it to `prometheus`.

Up to your performance SLA, you can call `start_http_server` from the main thread or, for better performance, you may want to use [pushgateway](https://github.com/prometheus/pushgateway) but that involves more setup and operation overhead.

The following example shows how to expose Prometheus metrics with HiQ.


```eval_rst
.. literalinclude:: ../../examples/prometheus/main_driver.py
   :language: python
   :emphasize-lines: 12, 21
   :linenos:
```

Run the driver code and visit `http://localhost:8681/metrics`, and we can see the metrics has been exposed. Please be noted that the metrics name has an `hiq_` as the prefix so that the metrics name is unique.


```eval_rst
.. thumbnail:: img/hiq_prometheus.jpg
```

We can see the summary of `main`, `func1`, `func2` exposed. If the prometheus server is running in the same host, you can add the config in prometheus.yml to scrape the metrics for user to query.

```yaml
  - job_name: "hiq"
    static_configs:
      - targets: ["localhost:8681"]
```
