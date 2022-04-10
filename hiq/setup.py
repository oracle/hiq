from setuptools import setup
import os

here = os.path.dirname(os.path.realpath(__file__))

VERSION = (
    "1.0.2"
    if "PKG_VERSION" not in os.environ or not os.environ["PKG_VERSION"]
    else os.environ["PKG_VERSION"]
)
DESCRIPTION = "HiQ - A Modern Observability System"

packages = [
    "hiq",
]


def read_file(filename: str):
    try:
        lines = []
        with open(filename) as file:
            lines = file.readlines()
            lines = [line.rstrip() for line in lines if not line.startswith('#')]
        return lines
    except:
        pass

LONG_DESCRIPTION = """
HiQ - A Modern Observability System
*************************************************

|Documentation Status| |CodeCov| |Github release| |lic|

HiQ is a ``declarative``, ``non-intrusive``, ``dynamic`` and
``transparent`` tracking system for both **monolithic** application and
**distributed** system. It brings the runtime information tracking and
optimization to a new level without compromising with speed and system
performance, or hiding any tracking overhead information. HiQ applies
for both I/O bound and CPU bound applications.

To explain the four features, **declarative** means you can declare the
things you want to track in a text file, which could be a json, yaml or
even csv,and no need to change program code. **Non-intrusive** means HiQ
doesn’t requires to modify original python code. **Dynamic** means HiQ
supports tracing metrics featuring at run time, which can be used for
adaptive tracing. **Transparent** means HiQ provides the tracing
overhead and doesn’t hide it no matter it is huge or tiny.

In addition to latency tracking, HiQ provides memory, disk I/O and
Network I/O tracking out of the box. The output can be saved in form of
normal line by line log file, or HiQ tree, or span graph.

Installation
------------

.. code:: bash

   pip install hiq-python

Get Started
-----------

Let start with a simplest example by running HiQ against a simple
monolithic python code `📄
main.py <https://github.com/oracle-samples/hiq/blob/main/hiq/examples/quick_start/main.py>`__:

.. code:: python

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

In this code, there is a simple chain of function calls: ``main()`` ->
``func1`` -> ``func2``.

Now we want to trace the functions without modifying its code. Let’s run
the following:

.. code:: python

   git clone https://github.com/oracle-samples/hiq.git
   cd hiq/examples/quick_start
   python main_driver.py

If everything is fine, you should be able to see the output like this:

.. figure:: https://raw.githubusercontent.com/oracle-samples/hiq/main/hiq/docs/source/img/main_driver.jpg

   An HiQ Simplest Example

From the screenshot we can see the timestamp and the latency of each
function:

=============== ====== ====== ====== ================
\               main   func1  func2  tracing overhead
=============== ====== ====== ====== ================
latency(second) 4.0045 4.0044 2.5026 0.0000163
=============== ====== ====== ====== ================

HiQ just traced the ``main.py`` file running without touching one line
of its code.

Documentation
-------------

**HTML**: `🔗 HiQ Online Document <https://hiq.readthedocs.io>`__, **PDF**: `🔗 HiQ PDF Document <https://github.com/oracle-samples/hiq/raw/main/hiq/docs/hiq.pdf>`__.

Examples
--------

Please check `🔗 examples <https://github.com/oracle-samples/hiq/tree/main/hiq/examples>`__ for usage examples.

Contributing
------------

HiQ welcomes contributions from the community. Before submitting a pull
request, please `review our 🔗 contribution guide <https://github.com/oracle-samples/hiq/blob/main/CONTRIBUTING.md>`__.

Security
--------

Please consult the `🔗 security guide <https://github.com/oracle-samples/hiq/blob/main/SECURITY.md>`__ for our
responsible security vulnerability disclosure process.

License
-------

Copyright (c) 2022 Oracle and/or its affiliates. Released under the
Universal Permissive License v1.0 as shown at
https://oss.oracle.com/licenses/upl/.

.. |image0| image:: https://raw.githubusercontent.com/oracle-samples/hiq/main/hiq/docs/source/_static/hiq.png
.. |Documentation Status| image:: https://readthedocs.org/projects/hiq/badge/?version=latest
   :target: https://hiq.readthedocs.io/en/latest/?badge=latest
.. |CodeCov| image:: https://codecov.io/gh/uber/athenadriver/branch/master/graph/badge.svg
   :target: https://hiq.readthedocs.io/en/latest/index.html
.. |Github release| image:: https://img.shields.io/badge/release-v1.0.0-red
   :target: https://github.com/uber/athenadriver/releases
.. |lic| image:: https://img.shields.io/badge/License-UPL--1.0-red
   :target: https://github.com/uber/athenadriver/blob/master/LICENSE
"""


setup(
    name="hiq-python",
    version=VERSION,
    author="Henry Fuheng Wu; Kathan Patel",
    author_email="<fuheng.wu@oracle.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    install_requires=read_file(f"{here}/requirements.txt"),
    keywords=[
        "hiq",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=packages,
    package_dir={"": "src"},
    package_data={"hiq": ["data/*.pk"]},
    url="https://github.com/oracle-samples/hiq",
)
