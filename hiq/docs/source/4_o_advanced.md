# HiQ Advanced Topics

The metrics described in the previous chapter are enough for most of the use cases for system metrics. To gain more insights on business metrics, you need to customize HiQ.

## Customized Tracing

HiQ is flexible so that you can customize it to trace other non-built-in metrics, such as business metrics. In order to customize it, you need to create your own class inheriting class `hiq.HiQSimple` and implement two functions `def custom(self)` and `def custom_disable(self)`.


### Log Metrics and Information to stdio

The following is a code example to demo how to log information, including business metrics, into terminal. The target code is a call chain from `main()`-> `func1()` -> `func2()`. The arguments for the main function are two dictionaries: `model` and `data`. We know the data input has two keys `img_path` and `size`, and we want to log the values corresponding to the keys.

Target Code:

```eval_rst
.. literalinclude:: ../../examples/custom/stdio/main.py
   :language: python
   :linenos:
```

Driver Code:

```eval_rst
.. literalinclude:: ../../examples/custom/stdio/main_driver.py
   :language: python
   :emphasize-lines: 9-15
   :linenos:
```

In the `custom()` function, we define a new function called `__my_main` which has the same signature of the target code's `main` function, and assign the target code's `main` to `self.o_main`, assign `__my_main` to the target code's `main`.

Inside the `__my_main` function, we check if there is img_path in the data argument. If there is, we log it. Finally we call `self.o_main` and return the result.

Run the driver code and get the output:

```
ℹ️  python examples/custom/stdio/main_driver.py
🌴 print log for img_path: /tmp/hello.jpg
🌴 print log for img_size: 1024
```
Without touching the target code, we logged one line of message into standard io console. This is useful for debugging purposes. We can also trace the information in HiQ Tree.


### Trace Metrics and Information In HiQ Tree


The target code will be the same as above. The difference here is we extract the information inside `__my_main` and define a function with decorator `@self._inserter_with_extra(extra={})`. `extra` will contain the information we want to trace. In this case, they are the image path and size.

Driver Code:

```eval_rst
.. literalinclude:: ../../examples/custom/hiqtree/main_driver.py
   :language: python
   :emphasize-lines: 10-18
   :linenos:
```

Run the driver code and get the output:

```
ℹ️  python examples/custom/hiqtree/main_driver.py
[2021-11-05 05:05:39.910686 - 05:05:43.914784]  [100.00%] 🟢_root_time(4.0041)
                                                            [{'img': '/tmp/hello.jpg', 'size': 1024}]
                                                            [OH:104us]
[2021-11-05 05:05:39.910686 - 05:05:43.914784]  [100.00%]    l___z(4.0041)
```

Under the tree's root node, we can see the image path information and image size metric.



## Log Monkey King

![HiQ Log Monkey King](img/lmk_cartoon_small.jpg)

LMK is a separate high performance logging system of HiQ. Sometimes we don't need the structural information of the trace, we just need to log data into a file in the disk. In this case, we can use LMK.

To use LMK, an environment variable `LMK` must be enabled.

### Log Metrics and Information to stdio

Without extra setup, LMK will print out logging information in stdio.

Target Code:

```eval_rst
.. literalinclude:: ../../examples/lmk/stdio/main.py
   :language: python
   :linenos:
```

Driver Code:

```eval_rst
.. literalinclude:: ../../examples/lmk/stdio/main_driver.py
   :language: python
   :emphasize-lines: 13
   :linenos:
```

At line 15, we set `LMK` equals to `1`, which enables log monkey king. Run the code we can get:

```
ℹ️  python examples/lmk/stdio/main_driver.py
2021-11-05 07:45:42.019567 - [time] [🆔 2418220] 🐵 [main]
2021-11-05 07:45:42.020127 - [time] [🆔 2418220] 🐵 [func1]
2021-11-05 07:45:43.521903 - [time] [🆔 2418220] 🐵 [func2]
2021-11-05 07:45:46.024517 - [time] [🆔 2418220] 🙈 [func2]
2021-11-05 07:45:46.024616 - [time] [🆔 2418220] 🙈 [func1]
2021-11-05 07:45:46.024635 - [time] [🆔 2418220] 🙈 [main]
```

The default log format is:
```text
time_stamp - [metric name] [process id] monkey [function name] [extra information]
```

🐵 means function call is started, and 🙈 means function call is completed.


### Log Metrics and Information to file

We can easily log the metrics and information into a file with LMK. LMK supports Python's built-in `logging` module and third party logging module like `loguru`.

#### Python built-in `logging` module

Target Code:

```eval_rst
.. literalinclude:: ../../examples/lmk/logging/main.py
   :language: python
   :linenos:
```

Driver Code:

```eval_rst
.. literalinclude:: ../../examples/lmk/logging/main_driver.py
   :language: python
   :emphasize-lines: 9-15, 19, 26
   :linenos:
```

- Explanation

Line 9-15: set up logging format, log file path and name  
Line 19: pass `logger` as `lmk_logger` when constructing HiQLatency Object


Run the driver code, then you can see the log has been written into file `/tmp/lmk.log`:

```
ℹ️  python examples/lmk/logging/main_driver.py
ℹ️  cat /tmp/lmk.log 
INFO 2021-11-05 17:03:57,581 - 2021-11-05 17:03:57.580419 - [time] [🆔 3568910] 🐵 [main]
INFO 2021-11-05 17:03:57,581 - 2021-11-05 17:03:57.581022 - [time] [🆔 3568910] 🐵 [func1]
INFO 2021-11-05 17:03:59,083 - 2021-11-05 17:03:59.082735 - [time] [🆔 3568910] 🐵 [func2]
INFO 2021-11-05 17:04:01,585 - 2021-11-05 17:04:01.585346 - [time] [🆔 3568910] 🙈 [func2]
INFO 2021-11-05 17:04:01,585 - 2021-11-05 17:04:01.585472 - [time] [🆔 3568910] 🙈 [func1]
INFO 2021-11-05 17:04:01,585 - 2021-11-05 17:04:01.585492 - [time] [🆔 3568910] 🙈 [main]
```

#### Third-party Logging Library Support

LMK supports third-party logging libraries which conforms to the standard logging protocol. One example is `loguru`. `loguru` is an easy-to-use, asynchronous, thread-safe, multiprocess-safe logging library. You can install it by running:

```
pip install loguru
```

The target code is the same as above. This is the driver Code:

```eval_rst
.. literalinclude:: ../../examples/lmk/loguru/main_driver.py
   :language: python
   :emphasize-lines: 4, 11, 19
   :linenos:
```

Run the driver code, you can see the information is printed in the terminal:

![](img/guru.jpg)


The same information is also stored in the log file:

```
ℹ️  cat /tmp/lmk_guru.log
2021-11-05 17:45:54.346 | INFO     | hiq.monkeyking:consumer:69 - 2021-11-05 17:45:54.346130 - [time] [🆔 3659097] 🐵 [main]
2021-11-05 17:45:54.347 | INFO     | hiq.monkeyking:consumer:69 - 2021-11-05 17:45:54.346699 - [time] [🆔 3659097] 🐵 [func1]
2021-11-05 17:45:55.848 | INFO     | hiq.monkeyking:consumer:69 - 2021-11-05 17:45:55.848450 - [time] [🆔 3659097] 🐵 [func2]
2021-11-05 17:45:58.351 | INFO     | hiq.monkeyking:consumer:69 - 2021-11-05 17:45:58.351059 - [time] [🆔 3659097] 🙈 [func2]
2021-11-05 17:45:58.351 | INFO     | hiq.monkeyking:consumer:69 - 2021-11-05 17:45:58.351163 - [time] [🆔 3659097] 🙈 [func1]
2021-11-05 17:45:58.351 | INFO     | hiq.monkeyking:consumer:69 - 2021-11-05 17:45:58.351182 - [time] [🆔 3659097] 🙈 [main]
```

## LumberJack


![Lumberjack](img/lumberjack.jpg)

Different form LMK, which writes log entry for each span, LumberJack is to handle an entire HiQ tree. For simplicity, we call it Jack. Jack is very useful in use cases where the overhead for processing metrics is so big that you cannot process each entry one by one. Kafaka is one Exmaple. Due to message encoding, network latency and response validation, a call to a Kafaka producer's `send_message` can easily take more than 1 second. Jack is a good way to handle Kafka message. We can send metrics tree to Kafka and process it later with an analytics server. This will be described in details in section [Integration with OCI Streaming](7_integration.html#oci-streaming).


Jack also writes a 500MB-rotated log in `~/.hiq/log_jack.log` unless you set environmental variable `NO_JACK_LOG`.

```
$ tail -n3 ~/.hiq/log_jack.log
time,v2,0,{"None":1637008247.9725869,1637008251.9771237,{"__main":1637008247.9725869,1637008251.9771237,{"__func1":1637008247.972686,1637008251.9771047,{"__func2":1637008249.4744177,1637008251.977021,}}}}
time,v2,0,{"None":1637008251.9785185,1637008255.9829764,{"__main":1637008251.9785185,1637008255.9829764,{"__func1":1637008251.978641,1637008255.982966,{"__func2":1637008253.480345,1637008255.9829247,}}}}
time,v2,0,{"None":1637008255.983492,1637008259.9854834,{"__main":1637008255.983492,1637008259.9854834,{"__func1":1637008255.9836354,1637008259.9854727,{"__func2":1637008257.485351,1637008259.9854305,}}}}
```


## Async and Multiprocessing in Python

- TODO
