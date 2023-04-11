# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

from hiq.utils import ts_to_dt, get_env_bool, lmk_data_handler
from hiq.constants import *
import os
import time
from multiprocessing import Process, Queue, Lock

import signal
import functools


# https://www.cloudcity.io/blog/2019/02/27/things-i-wish-they-told-me-about-multiprocessing-in-python/
class SignalObject:
    MAX_TERMINATE_CALLED = 3

    def __init__(self, shutdown_event):
        self.terminate_called = 0
        self.shutdown_event = shutdown_event


def default_signal_handler(
    signal_object, exception_class, signal_num, current_stack_frame
):
    signal_object.terminate_called += 1
    signal_object.shutdown_event.set()
    if signal_object.terminate_called == signal_object.MAX_TERMINATE_CALLED:
        raise exception_class()


def init_signal(signal_num, signal_object, exception_class, handler):
    handler = functools.partial(handler, signal_object, exception_class)
    signal.signal(signal_num, handler)
    signal.siginterrupt(signal_num, False)


"""
def init_signals(shutdown_event, int_handler, term_handler):
    signal_object = SignalObject(shutdown_event)
    init_signal(signal.SIGINT, signal_object, KeyboardInterrupt, int_handler)
    init_signal(signal.SIGTERM, signal_object, TerminateInterrupt, term_handler)
    return signal_object
"""


class LogMonkeyKing(object):
    """A multi-process Log Monkey"""

    @staticmethod
    def consumer_func(log_queue, lock, lmk_path, lmk_handler, logger):
        if os.cpu_count() >= 2 and os.uname().sysname == "Linux":
            affinity_list = list(os.sched_getaffinity(0))
            os.sched_setaffinity(0, set(affinity_list[len(affinity_list) // 2 :]))
        # Synchronize access to the console
        pid = os.getpid()
        # with lock:
        #    print("process 🐒 {}".format(pid))
        if lmk_path:
            if hasattr(logger, "add"):
                logger.add(lmk_path, rotation="500 MB")
        while True:
            # If the log_queue is empty, log_queue.get() will block until the log_queue has data
            data = log_queue.get()
            if data:
                if lmk_handler:
                    data = lmk_handler(data=data, pid=pid)
                else:
                    data = lmk_data_handler(data=data, pid=pid)
                with lock:
                    if logger:
                        logger.info(data)
                    else:
                        print(data)

    def __init__(sf, lmk_path=None, lmk_handler=None, lmk_logger=None, *args, **kwargs):
        # to use a cache ttl
        sf.summon_log_monkey_king = get_env_bool("LMK")
        if not sf.summon_log_monkey_king:
            sf.queue_lmk = sf.consumer = None
            return

        sf.queue_lmk = Queue()
        sf.lock = Lock()
        sf.consumer = Process(
            target=LogMonkeyKing.consumer_func,
            args=(sf.queue_lmk, sf.lock, lmk_path, lmk_handler, lmk_logger),
        )
        # This is critical! The consumer function has an infinite loop
        # Which means it will never exit unless we set daemon to true
        sf.consumer.daemon = True
        sf.consumer.start()

    def __del__(sf):
        sleep_count = 0
        if hasattr(sf, "queue_lmk"):
            while sf.queue_lmk and sf.queue_lmk.qsize() and sleep_count < 1:
                time.sleep(2)
                sleep_count += 1
        else:
            # TODO
            pass
        if hasattr(sf, "consumer"):
            if sf.consumer:
                print(sf.consumer)
                sf.consumer.join()
        else:
            # TODO
            pass

    # def tree_send_log_to_monkey(sf, **kwargs):
    #    sf.queue_lmk.put(kwargs)

    @staticmethod
    def __log(id_, extra, key, name, value):
        if len(name) >= 2 and name[:2] == "__":
            name = name[2:]
        _extra = dict(extra)
        monkey = "🐵" if key == EXTRA_START_TIME_KEY else "🙈"
        if key in _extra:
            del _extra[key]
            if not _extra:
                _extra = ""
            # metric here is actually the tree id
            print(
                f"{ts_to_dt(extra[key])} - [{id_}] [🆔 {os.getpid()}] {monkey} [{name}] {value} {_extra}"
            )
        else:
            if not _extra:
                _extra = ""
            if "time" in id_:
                value = ""
            print(
                f"{ts_to_dt(time.time())} - [{id_}] [🆔 {os.getpid()}] {monkey} [{name}] {value} {_extra}"
            )

    @staticmethod
    def log(id_: str, name: str, value, extra: dict, is_start=True, to_stdio=True):
        """log like a normal logger but with monkeyking

        Args:
            name: node name
            value (float or int): node value, it the value itself is time, there will be no time information in extra
            extra: extra information to log
        """
        if to_stdio:
            if is_start:
                LogMonkeyKing.__log(id_, extra, EXTRA_START_TIME_KEY, name, value)
            else:
                LogMonkeyKing.__log(id_, extra, EXTRA_END_TIME_KEY, name, value)
        else:
            pass


if __name__ == "__main__":
    import pickle

    lmk = LogMonkeyKing()
    print(lmk)
    d = pickle.dumps(lmk)
    lmk2 = pickle.loads(d)
    d2 = pickle.dumps(lmk2)
    print(d == d2)
