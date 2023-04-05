![](docs/../hiq/docs/source/_static/hiq.png) 🦉  Observability And Optimization In Modern AI Era
----
[![Documentation Status](https://readthedocs.org/projects/hiq/badge/?version=latest)](https://hiq.readthedocs.io/en/latest/?badge=latest)
[![CodeCov][cov-img]][cov]
[![Github release][release-img]][release]
[![lic][license-img]][license]

> 🔥 HiQ now supports GPU tracing, and supports DNN libraries like pyTorch, `transformers`, LAVIS, and LLM like T5 and GPT2 in addition to Onnxruntime, FastAPI and Flask.

HiQ is a `declarative`, `non-intrusive`, `dynamic` and `transparent` tracking system for both **monolithic** application and **distributed** system. It brings the runtime information tracking and optimization to a new level without compromising with speed and system performance, or hiding any tracking overhead information. HiQ applies for both I/O bound and CPU bound applications.

To explain the four features, **declarative** means you can declare the things you want to track in a text file, which could be a json, yaml or even csv,and no need to change program code. **Non-intrusive** means HiQ doesn't requires to modify original python code. **Dynamic** means HiQ supports tracing metrics featuring at run time, which can be used for adaptive tracing. **Transparent** means HiQ provides the tracing overhead and doesn't hide it no matter it is huge or tiny.

In addition to latency tracking, HiQ provides memory, disk I/O and Network I/O tracking out of the box. The output can be saved in form of normal line by line log file, or HiQ tree, or span graph.

HiQ's philosophy is to **decouple `observability logic` from `business logic`**. We don't have to enter the black hole to observe it. Do you like the idea? Leave a ⭐ if you enjoy the project and welcome to say Hi to us on [Slack 👋](https://join.slack.com/t/hiq-myo2317/shared_invite/zt-17ejh6ybo-51IX6G1lHMXgLbq2HKIO_Q)

[![Observability of Blackhole, NASA 2019](https://news.artnet.com/app/news-upload/2021/03/m87_lo_april11_polarimetric_average_image_ml_deband-cc-8bit-srgb-256x256.jpg)](https://www.nasa.gov/mission_pages/chandra/news/black-hole-image-makes-history)


## Installation

- Basic Installation

```bash
pip install hiq-python
```

- HiQ also supports extra installation

```bash
pip install hiq-python[fastapi] # To support fastapi web server online tracing
pip install hiq-python[gpu]     # To support GPU tracing, which will install pynvml
pip install hiq-python[lavis]   # To support Salesforce LAVIS Vision Language models
pip install hiq-python[transformers] # To support tracing Hugging Face's transformers library
pip install hiq-python[full]         # To support all the cases, and this will install all the dependency libraries
```


## Get Started

Let start with a simplest example by running HiQ against a simple monolithic python code [📄 `main.py`](hiq/examples/quick_start/main.py):

```python
# this is the main.py python source code
import time

def func1():
    time.sleep(1.5)
    print("func1")
    func2()

def func2():
    time.sleep(2.5)
    print("func2")

def main():
    func1()

if __name__ == "__main__":
    main()
```

In this code, there is a simple chain of function calls: `main()` -> `func1` -> `func2`.

Now we want to trace the functions without modifying its code. Let's run the following:


```python
git clone https://github.com/oracle-samples/hiq.git
cd hiq/examples/quick_start
python main_driver.py
```

If everything is fine, you should be able to see the output like this:

![HiQ Simplest Example](https://github.com/oracle/hiq/raw/main/hiq/docs/source/img/main_driver.jpg)

From the screenshot we can see the timestamp and the latency of each function:


|   | main  | func1  |  func2 |  tracing overhead |
|---|---|---|---|---|
| latency(second)  | 4.0045  | 4.0044  | 2.5026  | 0.0000163  |


HiQ just traced the `main.py` file running without touching one line of its code.

### HiQ UI

- Main Page

![HiQ UI Main Page](https://github.com/oracle/hiq/raw/main/hiq/docs/source/img/hiq-ui-1.png)

- Latency Details

![HiQ UI Latency Details](https://github.com/oracle/hiq/raw/main/hiq/docs/source/img/hiq-ui-2.png)

## Documentation

**HTML**: [🔗 HiQ Online Documents](https://hiq.readthedocs.io/en/latest/index.html)  | **PDF**: Please check [🔗 HiQ User Guide](https://github.com/oracle/hiq/blob/main/hiq/docs/hiq.pdf).

----

Logging: https://hiq.readthedocs.io/en/latest/4_o_advanced.html#log-monkey-king  
Tracing: https://hiq.readthedocs.io/en/latest/5_distributed.html  
- Zipkin: https://hiq.readthedocs.io/en/latest/5_distributed.html#zipkin   
- Jaeger: https://hiq.readthedocs.io/en/latest/5_distributed.html#jaeger   

Metrics:  
- Prometheus: https://hiq.readthedocs.io/en/latest/7_integration.html#prometheus  

Streaming:  
- Kafka: https://hiq.readthedocs.io/en/latest/7_integration.html#oci-streaming 

## DNN Model Observability & Visualization

HiQ can visualize DNN model. To get the following BERT model's structure, you can just run:

```
python -m hiq.vis
```

![BERT](https://raw.githubusercontent.com/henrywoo/hiq/main/hiq/docs/medium/vis_bert.png)

The graph is self-explantory. There are several conventions:

- ❄️ means frozen layer, where `requires_grad` is false.
- 📈 means gradient exists for that model parameter, which usually happens after backpopulation.
- `+`, bold font, and underscored dotted line mean the displayed layer is a folded version of multiple layers with the same structure.

What you need to do is just calling `print_model(model)` in your code. Refer to: [here](https://github.com/henrywoo/hiq/tree/main/hiq/examples/vis) for how to use it.

## Jupyter NoteBook

HiQ was originally developed to find Onnxruntime performance bottleneck in DNN inference, and it works well for other computation intensive applications too. The following are two examples.

### Add Observability to PaddlePaddle (PaddleOCR)

- [Latency](https://github.com/oracle-samples/hiq/blob/main/hiq/examples/paddle/demo.ipynb)
- [Memory](https://github.com/oracle-samples/hiq/blob/main/hiq/examples/paddle/demo_memory.ipynb)

- Latency Gantt Chart

![Latency Gantt Chart](https://raw.githubusercontent.com/oracle/hiq/main/hiq/docs/medium/hiq-gantt.png)

- HiQ Call Graph

![HiQ Call Graph](https://raw.githubusercontent.com/oracle/hiq/main/hiq/docs/medium/hiq-call-graph.png)

### Add Observability to Onnxruntime (AlexNet)

- [Latency](https://github.com/oracle-samples/hiq/blob/main/hiq/examples/onnxruntime/demo.ipynb)
- [Intrusive](https://github.com/oracle-samples/hiq/blob/main/hiq/examples/onnxruntime/demo_intrusive.ipynb)


## Examples

Please check [🔗 examples](https://github.com/oracle/hiq/blob/main/hiq/examples) for usage examples.

## Contributing


HiQ welcomes contributions from the community. Before submitting a pull request, please [review our 🔗 contribution guide](https://github.com/oracle/hiq/blob/main/CONTRIBUTING.md).



## Security

Please consult the [🔗 security guide](https://github.com/oracle/hiq/blob/main/SECURITY.md) for our responsible security vulnerability disclosure process.


## License

Copyright (c) 2022 Oracle and/or its affiliates. Released under the Universal Permissive License v1.0 as shown at <https://oss.oracle.com/licenses/upl/>.

## Presentation and Demos

- [Introduction to Observability with HiQ](https://github.com/oracle-samples/hiq/blob/main/hiq/docs/Introduction-To-Observability-With-HiQ.pdf)

[cov-img]: https://codecov.io/gh/uber/athenadriver/branch/master/graph/badge.svg
[cov]: https://hiq.readthedocs.io/en/latest/index.html

[release-img]: https://img.shields.io/badge/release-v1.1.9-red
[release]: https://github.com/oracle-samples/hiq

[license-img]: https://img.shields.io/badge/License-UPL--1.0-red
[license]: https://github.com/oracle-samples/hiq/blob/main/LICENSE.txt

[release-policy]: https://golang.org/doc/devel/release.html#policy

