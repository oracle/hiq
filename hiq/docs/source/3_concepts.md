# HiQ Core Concepts

## Target Code

The main program which we want to collect information about. It could be a runnable python code or a module.

## Driver Code

HiQ driver code is like agent in most APM applications, but there is a little difference. With agent, a runnable application is needed, so that the agent can attach to it. But driver code can work with modules too. For instance, you can write python function in driver code to call another target function in the target module.

## HiQ Tracing Class/Object

HiQ provides two Tracing Class out of the box: `HiQLatency` for latency tracing and `HiQMemory` for memory tracing. You can derive from `HiQSimple` to have you own customized tracing. These classes are called `HiQ Tracing Class` and the object is called `HiQ Tracing Object`.

## LumberJack/Jack

LumberJack is a process to collect traces, HiQ trees in this case, to send to HiQ server. To enable LumberJack, set environment variables `JACK` to 1.

## Log Monkey King

Log Monkey King is a process to write traditional semi-structured, append-only log into log files. To enable Log Monkey King, set environment variables `LMK` to 1.

## HiQ Tree

HiQ tree is a nary tree, plus a stack and dictionary/map. Different from the traditional BST, AVL, RB Tree, the tree is a strictly insertion-time-ordered tree from top to bottom and from left to right, so you can not switch the order of the nodes. The purpose of the tree is not for searching, or sorting. It is for visualizing program execution and facilitating code optimization. The values inserted into the tree doesn't need to be monotonically increasing.

Every node in an HiQ tree has a start value and a end value. `end` value minus `start` value is equal to the span of the node, or sometimes you can just call the node itself as a `span` to conform with OpenTracing conventions.


HiQ tree has three `mode`s. When HiQ tree is in `concise` mode, which is the default mode, HiQ tree will not contain ZSP(zero-span node). When the mode is `verbose` mode, HiQ tree can have ZSP if there is no extra information in the node, like exception information. When the mode is `debug`, all the zero span node will be recorded as well.



## HiQ Conf

HiQ conf could be a text configuration file to specify the functions you want to trace. It can be json or CSV file.

A sample json file is like:

```
    [
        {
            "name": "f1",
            "module": "my_model2",
            "function": "func1",
            "class": ""
        },
        {
            "name": "f2",
            "module": "my_model2",
            "function": "func2",
            "class": ""
        },
        {
            "name": "f3",
            "module": "my_model2",
            "function": "func3",
            "class": ""
        },
        {
            "name": "f4",
            "module": "my_model2",
            "function": "func4",
            "class": ""
        }
    ]
```

A sample csv file is like:
```
    "my_model2", "", "func1", "f1"
    "my_model2", "", "func2", "f2"
    "my_model2", "", "func3", "f3"
    "my_model2", "", "func4", "f4"
```

Also you can also use a list of list to represent it. For example, an equivalent representation of the above json and csv file is:

```
[
    ["my_model2", "", "func1", "f1"],
    ["my_model2", "", "func2", "f2"],
    ["my_model2", "", "func3", "f3"],
    ["my_model2", "", "func4", "f4"]
]
```

The inner list must have length of 4. They are: `[module_name, class_name, function_name, tag_name]`. The tag name will display in the HiQ as the tree node name.

The following example shows how to use HiQ conf.

Target Code:

```eval_rst
.. literalinclude:: ../../examples/conf/main.py
   :language: python
   :linenos:
```

Driver Code:

```eval_rst
.. literalinclude:: ../../examples/conf/main_driver.py
   :language: python
   :linenos:
```

HIQ Conf:

```eval_rst
.. literalinclude:: ../../examples/conf/hiq.conf
   :language: python
   :linenos:
```

Run the driver code you will get something like:

```
ℹ️  python hiq/examples/conf/main_driver.py
func1
func2
[2021-11-03 22:51:08.946615 - 22:51:12.951082]  [100.00%] 🟢_root_time(4.0045)
                                                            [OH:191us]
[2021-11-03 22:51:08.946615 - 22:51:12.951082]  [100.00%]    l___main(4.0045)
[2021-11-03 22:51:08.946663 - 22:51:12.951069]  [100.00%]       l___func1(4.0044)
[2021-11-03 22:51:10.448407 - 22:51:12.951018]  [ 62.50%]          l___func2(2.5026)
```

## Latency Overhead

**All runtime monitoring has overhead**, no matter latency or memory, CPU. In most cases, we care about latency overhead. Different from all the open source projects in the community and the products in the market, HiQ provides transparent latency overhead information out of the box.

In the quick start example, we can see the latency overhead is printed out under the tree's root node, which is 163us, and equivalent to 0.04% of the total running time.

![](img/main_driver.jpg)



