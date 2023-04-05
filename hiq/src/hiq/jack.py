# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import os
from multiprocessing import Process, Queue, Lock
from hiq.utils import _check_overhead, get_env_bool, ensure_folder, get_home
import time


def get_jack_log_file():
    log_file = f"{get_home()}/.hiq/log_jack.log"
    try:
        ensure_folder(log_file)
        return log_file
    except PermissionError as e:
        pass
    try:
        log_file = f"{os.getcwd()}/.hiq/log_jack.log"
        ensure_folder(log_file)
        return log_file
    except PermissionError as e:
        pass
    log_file = f".hiq/log_jack.log"
    ensure_folder(log_file)
    return log_file


def log_jack_rotated(
    log_file=get_jack_log_file(),
    max_bytes=500 * 1024 * 1024,
    backup_count=20,
):
    if get_env_bool("NO_JACK_LOG"):
        return None
    import logging
    from logging.handlers import RotatingFileHandler

    my_handler = RotatingFileHandler(
        log_file,
        mode="a",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding=None,
        delay=0,
    )
    my_handler.setLevel(logging.INFO)

    app_log = logging.getLogger("root")
    app_log.setLevel(logging.INFO)
    app_log.addHandler(my_handler)
    return app_log


def get_kafka():
    if get_env_bool("HIQ_OCI_STREAMING"):
        from hiq.vendor_oci_streaming import OciStreamingClient

        return OciStreamingClient()
    return None


class Jack(object):
    """Jack is a lumberjack to send trees to remote HiQ server in his own process space
    Jack is disabled by default. To enable it, set env variable JACK=1:
        export JACK=1
    """

    @staticmethod
    def consumer_func(queue, lock):
        if os.cpu_count() >= 2 and os.uname().sysname == "Linux":
            affinity_list = list(os.sched_getaffinity(0))
            os.sched_setaffinity(0, set(affinity_list[len(affinity_list) // 2 :]))

        pid = os.getpid()
        logger = log_jack_rotated()
        kafka_client = get_kafka()
        with lock:
            print("🅹 🅰 🅒 Ⓚ {} is started".format(pid))
        while True:
            try:
                data = queue.get()
                for key, value in data.items():
                    """
                    tree = Tree(value)
                    itree._itree.consolidate(tree.root)
                    # tree.show()
                    data = tree.repr()
                    """
                    if logger:
                        logger.info(key + "," + value)
                    if kafka_client:
                        kafka_client.produce_messages(key, value)
                    # with lock:
                    #    print(k, t)
                    #    print("🅹 {} got {} {}".format(pid, key, data))
            except Exception as e:
                time.sleep(0.1)
                print(e)

    def __init__(sf, *args, **kwargs):
        sf.invite_jack = get_env_bool("JACK")
        if not sf.invite_jack:
            sf.queue_jack = sf.consumer = None
            return
        sf.queue_jack = Queue()
        sf.lock = Lock()
        sf.consumer = Process(target=Jack.consumer_func, args=(sf.queue_jack, sf.lock))
        # This is critical! The consumer function has an infinite loop
        # Which means it will never exit unless we set daemon to true
        sf.consumer.daemon = True
        sf.consumer.start()

    def __del__(sf):
        if sf.consumer:
            sf.consumer.join()

    @_check_overhead
    def send_trees_to_jack(sf, d: dict, debug=False):
        if not sf.queue_jack:
            if debug:
                print("Jack is working")
            return
        data = {}
        for k, val in d.items():
            data[k] = val.repr()
        sf.queue_jack.put_nowait(data)
