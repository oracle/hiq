# HiQ API

## HiQ Classes


```eval_rst
 .. autoclass:: hiq.base.HiQBase

    .. automethod:: __init__
    .. automethod:: enable_hiq
    .. automethod:: disable_hiq
    .. automethod:: get_overhead
    .. automethod:: get_overhead_us
    .. automethod:: get_overhead_pct
    .. automethod:: custom
    .. automethod:: custom_disable
    .. automethod:: set_extra_metrics


 .. autoclass:: hiq.base.HiQLatency

 .. autoclass:: hiq.base.HiQMemory

 .. autoclass:: hiq.base.HiQSimple
 ```

----

## Integration Classes

```eval_rst
 .. autoclass:: hiq.vendor_oci_apm.OciApmHttpTransport

 .. autoclass:: hiq.vendor_oci_apm.HiQOciApmContext

    .. automethod:: __init__

 .. autoclass:: hiq.server_flask_with_oci_apm.FlaskWithOciApm

```

## Distributed Tracing

```eval_rst
  .. autofunction:: hiq.distributed.setup_jaeger

  .. autofunction:: hiq.distributed.HiQOpenTelemetryContext
```

----


## Metrics Client

```eval_rst
 .. autoclass:: hiq.http_metric_client.HttpMetricsClient

    .. automethod:: __init__

    .. automethod:: timing_metric_data

    .. automethod:: wrap_metric_data

    .. automethod:: submit_metrics_queue

    .. automethod:: gauge_metric

    .. automethod:: timing_metric

    .. automethod:: get

```

----

## Utility Functions

```eval_rst
  .. autofunction:: hiq.get_global_hiq_status

  .. autofunction:: hiq.set_global_hiq_status

  .. autofunction:: hiq.mod

  .. autoclass:: hiq.HiQStatusContext

      .. automethod:: __init__

  .. warning::
     `hiq.HiQStatusContext` is not multi-thread and multi-processing safe.

  .. autoclass:: hiq.SingletonMeta

  .. autoclass:: hiq.SingletonBase

  .. autoclass:: hiq.SilencePrint

  .. autofunction:: hiq.read_file

  .. autofunction:: hiq.write_file

  .. autofunction:: hiq.execute_cmd

  .. autofunction:: hiq.download_from_http

  .. autofunction:: hiq.ensure_folder

  .. autofunction:: hiq.get_env_bool

  .. autofunction:: hiq.get_env_int

  .. autofunction:: hiq.get_env_float

  .. autofunction:: hiq.lmk_data_handler

  .. autofunction:: hiq.get_home
   
  .. autofunction:: hiq.get_proxies

  .. autofunction:: hiq.random_str

  .. autofunction:: hiq.memoize

  .. autofunction:: hiq.memoize_first

  .. autofunction:: hiq.is_hiqed

  .. autofunction:: hiq.get_memory_mb

  .. autofunction:: hiq.get_memory_kb

  .. autofunction:: hiq.get_memory_b

  .. autofunction:: hiq.ts_pair_to_dt

  .. autofunction:: hiq.ts_to_dt

  .. autofunction:: hiq.utc_to_pst

  .. autofunction:: hiq.get_graph_from_string

  .. autofunction:: hiq.get_duration_from_hiq_string
 ```
