```eval_rst
Welcome to HiQ's documentation!
===============================


.. toctree::
   :maxdepth: 2
   :hidden:

   2_background
   3_concepts
   4_basics
   4_o_advanced
   5_distributed
   7_integration
   8_faq
   x_ref
   6_api
```

![](_static/hiq.png)
----
[![Documentation Status](https://readthedocs.org/projects/hiq/badge/?version=latest)](https://hiq.readthedocs.io/en/latest/?badge=latest)

HiQ is a `declarative`, `non-intrusive`, `dynamic` and `transparent` tracking system for both **monolithic** application and **distributed** system. It brings the runtime information tracking and optimization to a new level without compromising with speed and system performance, or hiding any tracking overhead information. HiQ applies for both I/O bound and CPU bound applications.

To explain the four features, **declarative** means you can declare the things you want to track in a text file, which could be a json, yaml or even csv,and no need to change program code. **Non-intrusive** means HiQ doesn't requires to modify original python code. **Dynamic** means HiQ supports tracing metrics featuring at run time, which can be used for adaptive tracing. **Transparent** means HiQ provides the tracing overhead and doesn't hide it no matter it is huge or tiny.

In addition to latency tracking, HiQ provides memory, disk I/O and Network I/O tracking out of the box. The output can be saved in form of normal line by line log file, or HiQ tree, or span graph.


## Installation


```bash
pip install py-hiq
```


## Get Started

To use HiQ, you need to have `target code` and `driver code`.

![](hiq/docs/source/img/driver.jpg)

Let start with a simplest example by running HiQ against a monolithic application. The target code is `main.py`:

```python
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

In this target code, there is a simple chain of function calls: `main()` -> `func1` -> `func2`. We can actually run the target code:

```python
cd examples
python main.py
```

And the output should be:

```
func1
func2
```

Now let's run the driver code, and if everything is fine, you should be able to see the output like this:

![HiQ Simplest Example](img/main_driver.jpg)

- Explanation of driver code

```python
import hiq


def run_main():
    driver = hiq.HiQLatency(
        hiq_table_or_path=[
            ["main", "", "main", "main"],
            ["main", "", "func1", "func1"],
            ["main", "", "func2", "func2"],
        ]
    )
    hiq.mod("main").main()
    driver.show()


if __name__ == "__main__":
    run_main()
```

Line 1: import python module `hiq`.  
Line 5-11: create an object of class `hiq.HiQLatency` and declare we want to trace function `main()`, `func1()`, `func2()` in `main.py`.  
Line 12: call function `main()` in `main.py`.  
Line 13: print HiQ trees.


## Documentation

**HTML**: [🔗 HiQ Online Documents](https://hiq.readthedocs.io/en/latest/index.html)  
**PDF**: Please check [🔗 HiQ User Guide](https://github.com/oracle-samples/hiq/blob/main/hiq/docs/hiq.pdf).

## Examples

Please check [🔗 examples](https://github.com/oracle-samples/hiq/blob/main/hiq/examples) for usage examples.

## Contributing


HiQ welcomes contributions from the community. Before submitting a pull request, please [review our 🔗 contribution guide](https://github.com/oracle-samples/hiq/blob/main/CONTRIBUTING.md).



## Security

Please consult the [🔗 security guide](https://github.com/oracle-samples/hiq/blob/main/SECURITY.md) for our responsible security vulnerability disclosure process.

## License

Copyright (c) 2022 Oracle and/or its affiliates. Released under the Universal Permissive License v1.0 as shown at <https://oss.oracle.com/licenses/upl/>.





```eval_rst
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

```
