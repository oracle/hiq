![](docs/../hiq/docs/source/_static/hiq.png)
----
[![Documentation Status](https://readthedocs.org/projects/hiq/badge/?version=latest)](https://hiq.readthedocs.io/en/latest/?badge=latest)
[![CodeCov][cov-img]][cov]
[![Github release][release-img]][release]
[![lic][license-img]][license]


HiQ is a `declarative`, `non-intrusive`, `dynamic` and `transparent` tracking system for both **monolithic** application and **distributed** system. It brings the runtime information tracking and optimization to a new level without compromising with speed and system performance, or hiding any tracking overhead information. HiQ applies for both I/O bound and CPU bound applications.

To explain the four features, **declarative** means you can declare the things you want to track in a text file, which could be a json, yaml or even csv,and no need to change program code. **Non-intrusive** means HiQ doesn't requires to modify original python code. **Dynamic** means HiQ supports tracing metrics featuring at run time, which can be used for adaptive tracing. **Transparent** means HiQ provides the tracing overhead and doesn't hide it no matter it is huge or tiny.

In addition to latency tracking, HiQ provides memory, disk I/O and Network I/O tracking out of the box. The output can be saved in form of normal line by line log file, or HiQ tree, or span graph.


## Installation


```bash
pip install py-hiq
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

![HiQ Simplest Example](hiq/docs/source/img/main_driver.jpg)

From the screenshot we can see the timestamp and the latency of each function:


|   | main  | func1  |  func2 |  tracing overhead |
|---|---|---|---|---|
| latency(second)  | 4.0045  | 4.0044  | 2.5026  | 0.0000163  |


HiQ just traced the `main.py` file running without touching one line of its code.

## Documentation

**HTML**: [🔗 HiQ Online Documents](https://hiq.readthedocs.io/en/latest/index.html)  
**PDF**: Please check [🔗 HiQ User Guide](hiq/docs/hiq.pdf).

## Examples

Please check [🔗 examples](hiq/examples) for usage examples.

## Contributing


HiQ welcomes contributions from the community. Before submitting a pull request, please [review our 🔗 contribution guide](./CONTRIBUTING.md).



## Security

Please consult the [🔗 security guide](./SECURITY.md) for our responsible security vulnerability disclosure process.

## License

Copyright (c) 2022 Oracle and/or its affiliates. Released under the Universal Permissive License v1.0 as shown at <https://oss.oracle.com/licenses/upl/>.


[cov-img]: https://codecov.io/gh/uber/athenadriver/branch/master/graph/badge.svg
[cov]: https://hiq.readthedocs.io/en/latest/index.html

[release-img]: https://img.shields.io/badge/release-v1.0.0-red
[release]: https://github.com/uber/athenadriver/releases

[report-card-img]: https://goreportcard.com/badge/github.com/uber/athenadriver
[report-card]: https://goreportcard.com/report/github.com/uber/athenadriver

[license-img]: https://img.shields.io/badge/License-UPL--1.0-red
[license]: https://github.com/uber/athenadriver/blob/master/LICENSE

[release-policy]: https://golang.org/doc/devel/release.html#policy

