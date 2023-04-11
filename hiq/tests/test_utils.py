# HiQ version 1.0.
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import os
import sys
import pytest
from typing import Callable
import io
from contextlib import redirect_stdout

cur_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.abspath(os.path.join(cur_dir, "../src/hiq")))

from utils import *


def test_execute_cmd():
    file_name = random_str()
    execute_cmd(f"touch {file_name}")
    assert os.path.isfile(file_name)
    execute_cmd(
        f"rm {file_name}",
        verbose=False,
        check=True,
        stderr_log=open("data/error.log", "a+"),
        debug=True,
    )
    assert os.path.exists(file_name) == False

    file_name = random_str()
    execute_cmd(f"touch {file_name}", split=False)
    assert os.path.isfile(file_name)
    execute_cmd(
        f"rm {file_name}",
        verbose=True,
        check=False,
        shell=False,
        stderr_log=open("data/error.log", "a+"),
        debug=False,
    )
    assert os.path.exists(file_name) == False

    f = io.StringIO()
    with redirect_stdout(f):
        execute_cmd("sleep 1m", split=False, timeout=2)
    out = f.getvalue()
    assert "timed-out" in out


def test_utc_to_pst():
    with pytest.raises(ValueError) as error_info:
        utc_to_pst("2021-12-16")
    assert "ValueError" in str(error_info)
    assert utc_to_pst("2021-06-19T20:32:18+0000") == "2021-06-19 13:32:18-07:00"


def test_ts_to_dt():  # datetime.fromtimestamp() works differently in different IDEs. Perhaps we need to set a timezone.
    timestamp = 1638970909.806089
    assert ts_to_dt(0.0) == str(0.0)
    assert (
        ts_to_dt(timestamp) == "2021-12-08 13:41:49.806089"
    )  # "2021-12-08 19:11:49.806089"


def test_ts_pair_to_dt():  # datetime.fromtimestamp() works differently in different IDEs. Perhaps we need to set a timezone.
    ts1 = 1638972804.2896547
    ts2 = 1638972804.289656
    assert ts_pair_to_dt(ts1, ts2) == "2021-12-08 19:43:24.289655 - 19:43:24.289656"
    ts1 = 1638972804.2896547
    ts2 = 1637972804.289656
    assert (
        ts_pair_to_dt(ts1, ts2)
        == "2021-12-08 19:43:24.289655 - 2021-11-27 05:56:44.289656"
    )


def test_read_file():
    def filter_message(x):
        words = ["ORACLE", "Cloud", "Infrastructure", "Welcome to ORACLE"]
        if x in words:
            return True
        else:
            return False

    with pytest.raises(ValueError) as error_info:
        assert read_file(os.getcwd(), raise_=False) == None
        read_file(os.getcwd(), raise_=True)
    assert "not a file" in str(error_info)
    assert (
        read_file(
            os.path.join(os.getcwd(), "data/helloworld"), binary_mode=True, strip=True
        )
        == b"Welcome to ORACLE\noracle cloud infrastructure"
    )
    assert read_file(
        os.path.join(os.getcwd(), "data/sample.json"), as_json=True, binary_mode=True
    ) == {"date": "2021-09-21T04:52:51+0000", "eventKey": "repo:refs_changed"}
    assert read_file(
        os.path.join(os.getcwd(), "data/helloworld"),
        binary_mode=False,
        by_line=True,
        filter_func=filter_message,
    ) == ["Welcome to ORACLE"]


def test_write_file():
    name = random_str()
    write_file(
        os.path.join(cur_dir, "data/sample"),
        data="hello",
        as_owner=name,
        as_group=name,
        append=False,
    )
    assert open(os.path.join(cur_dir, "data/sample")).read() == "hello"
    write_file(
        os.path.join(cur_dir, "data/sample"),
        data="hello",
        as_owner=name,
        as_group=name,
        append=True,
    )
    assert open(os.path.join(cur_dir, "data/sample")).read() != "hello"
    write_file(
        os.path.join(cur_dir, "data/sample"),
        data="hello",
        as_owner=name,
        as_group=name,
        append=False,
    )
    assert open(os.path.join(cur_dir, "data/sample")).read() == "hello"


def test_ensure_folder():
    assert ensure_folder(os.path.realpath(__file__)) == cur_dir
    assert ensure_folder(os.path.join(cur_dir, random_str())) == cur_dir


def test_download_from_http():
    # Test for IOError
    with pytest.raises(IOError) as error_info:
        download_from_http(
            uri="https://www.google.com/idontexist",
            local_file_path=os.path.join(cur_dir, ""),
        )
        assert "Error" in error_info

    # Test for successful download
    uri_path_ico = "https://www.google.com/favicon.ico"
    downloaded_ico = download_from_http(
        uri=uri_path_ico,
        local_file_path=os.path.join(cur_dir, "data/downloadfromhttp_googleicon.ico"),
        display=False,
    )
    assert (
        open("data/googleicon.ico", "rb").read() == open(downloaded_ico, "rb").read()
    )  # test for icon

    # Test for ValueError.
    with pytest.raises(ValueError) as error_info:
        download_from_http(
            uri=uri_path_ico,
            local_file_path=os.path.join(
                cur_dir, "data/downloadfromhttp_googleicon.ico"
            ),
            display=True,
        )
        assert (
            "error" in error_info
        )  # Due to no Content-Encoding we have progress_bar.n!=total_size_in_bytes

    # Test for total_size_in_bytes<=0
    uri_path_empty = (
        "https://objectstorage.us-ashburn-1.oraclecloud.com/"
        "p/vtT9R2oK8cD_9m86Q68X7uBNKDKLUGLu9Fvh0FdNT804xhsiVqZqOno8XfjG-GDV/"
        "n/ax3dvjxgkemg/b/test-download-from-http/o/emptyfile"
    )
    downloaded_empty = download_from_http(
        uri=uri_path_empty,
        local_file_path=os.path.join(cur_dir, "data/downloadfromhttp_empty"),
        display=True,
    )
    assert open(downloaded_empty).read() == ""

    assert (
        open("data/googleicon.ico", "rb").read()
        == open(
            download_from_http(
                uri=uri_path_ico,
                local_file_path=os.path.join(
                    cur_dir, "data/downloadfromhttp_googleicon.ico"
                ),
                display=True,
            )
        ).read()
    )


def test_random_str():
    assert len(random_str()) == 12
    assert len(random_str(15)) == 15
    assert type(random_str()) == type("str")


def test_get_proxies():
    os.environ["http_proxy"] = "154.136.68.91"
    assert get_proxies() == {
        "http": "154.136.68.91",
        "https": "",
        "ftp": "",
        "no_proxy": "",
    }


def test_get_env_bool():
    os.environ["ZERO"] = "0"
    os.environ["EMPTY_STRING"] = ""
    os.environ["NON_EMPTY_STRING"] = random_str()
    os.environ["NON_ZERO_NUMERIC"] = "1729"
    assert get_env_bool("ZERO") == False
    assert get_env_bool("EMPTY_STRING") == False
    assert get_env_bool("NON_EMPTY_STRING") == True
    assert get_env_bool("NON_ZERO_NUMERIC") == True


def test_get_env_int():
    os.environ["INTEGER_STRING"] = "10"
    assert get_env_int("INTEGER_STRING") == 10


def test_get_env_float():
    os.environ["FLOAT_STRING"] = "17.29"
    assert get_env_float("FLOAT_STRING") == 17.29


def test_is_hiqed():  # isn't working for functions not in hiq
    assert is_hiqed(Callable[[], str], "read") == True
    assert is_hiqed(Callable[[], str], random_str()) == False


def test_lmk_data_handler():
    data = {
        "id_": "",
        "name": "",
        "value": "",
        "extra": {"time": 1638970909.806089},
        "is_start": {},
    }
    assert (
        lmk_data_handler(data)
        == "2021-12-08 19:11:49.806089 - [] [🆔 "
        + str(os.getpid())
        + "] 🙈 []  {'time': 1638970909.806089}"
    )
    data = {
        "id_": "",
        "name": "",
        "value": 1638970909.806089,
        "extra": {"msg": "logging successful"},
        "is_start": "",
    }
    assert (
        lmk_data_handler(data)
        == "2021-12-08 19:11:49.806089 - [] [🆔 "
        + str(os.getpid())
        + "] 🙈 [] {'msg': 'logging successful'}"
    )
    data = {
        "id_": "",
        "name": "",
        "value": 1638970909.806089,
        "extra": {},
        "is_start": "",
    }
    assert (
        lmk_data_handler(data)
        == "2021-12-08 19:11:49.806089 - [] [🆔 " + str(os.getpid()) + "] 🙈 []"
    )


def test_get_home():
    assert get_home() == os.getenv("HOME")


def test_memoize_first():
    from timeit import default_timer as timer

    @memoize
    def fib(n, msg):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fib(n - 1, random_str()) + fib(n - 2, random_str())

    start = timer()
    res = fib(5, random_str())
    end = timer()
    time = end - start

    @memoize_first
    def fib(n, msg):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fib(n - 1, random_str()) + fib(n - 2, random_str())

    start = timer()
    res_first = fib(5, random_str())
    end = timer()
    time_first = end - start

    assert time >= time_first and res == res_first == 5
    assert fib(0, random_str()) == 0
    assert fib(1, random_str()) == 1


def test_memoize():
    from timeit import default_timer as timer

    @memoize
    def fib(n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fib(n - 1) + fib(n - 2)

    start = timer()
    res_1 = fib(50)
    end = timer()
    time_1 = end - start

    start = timer()
    res_2 = fib(50)
    end = timer()
    time_2 = end - start

    assert (time_1 >= time_2) and (res_1 == res_2 == 12586269025)
    assert fib(1) == 1
    assert fib(0) == 0


def test_gantt_chart():
    # test gantt_chart for tau
    tau1 = """t1^time,,0,42,3,1,1e-07,954#{'overhead_start': 0, 'overhead': 7007, 'img_path': '/opt/airflow/workspace/web/dataset/golden/vision_service_document_classification/DIC_Golden_test_set/Invoice/Image_from_iOS.jpg', 'result': '{"pages": [{"detectedDocumentTypes": [{"documentType": "Invoice", "confidence": 0.9984438419342041}, {"documentType": "Payslip", "confidence": 0.0008064216235652566}, {"documentType": "Taxform", "confidence": 0.0005774341407231987}, {"documentType": "Bank_Statement", "confidence": 7.192217890406027e-05}, {"documentType": "Receipt", "confidence": 6.365847366396338e-05}, {"documentType": "Resume", "confidence": 2.9998378522577696e-05}, {"documentType": "Others", "confidence": 6.4818650571396574e-06}, {"documentType": "Passport", "confidence": 1.5685918697272427e-07}, {"documentType": "Driver_license", "confidence": 9.681562573859992e-08}, {"documentType": "Check", "confidence": 5.857019047539325e-08}]}], "documentClassificationModelVersion": "1.1.12"}'}%n1*[None,inf,inf,0$0#[_ort_sess,1639356985.5702672,1639356985.5965557,0$0#][_ort_sess,1639356985.5970273,1639356985.6713126,0$0#][_ort_sess,1639356985.6717696,1639356985.7470868,0$0#][_ort_sess,1639356985.7472188,1639356985.7536354,0$0#][_ort_sess,1639356985.753862,1639356985.8217947,0$0#][_ort_sess,1639356985.8222127,1639356985.9028614,0$0#][_ort_sess,1639356985.9089844,1639356985.995218,0$0#][_ort_sess,1639356986.0040185,1639356986.7499647,0$0#][_ort_sess,1639356986.7505062,1639356986.8649836,0$0#][_ort_sess,1639356986.865604,1639356986.9432395,0$0#][_ort_sess,1639356986.9437199,1639356987.0212493,0$0#][_ort_sess,1639356987.0217955,1639356987.0993128,0$0#][_ort_sess,1639356987.0998278,1639356987.1781304,0$0#][_ort_sess,1639356987.1825173,1639356987.2641575,0$0#][_ort_sess,1639356987.2647128,1639356987.3802774,0$0#][_ort_sess,1639356987.3808477,1639356987.426587,0$0#][__predict,1639356987.4268615,1639356989.9975772,0$0#[__ort,1639356987.7654493,1639356987.7666342,0$0#][__ort,1639356987.8104374,1639356987.9363396,0$0#][__ort,1639356988.2967083,1639356988.350306,0$0#][__ort,1639356988.3552182,1639356988.4045203,0$0#][__ort,1639356988.408631,1639356988.4571812,0$0#][__ort,1639356988.462387,1639356988.5149536,0$0#][__ort,1639356988.5198474,1639356988.5765593,0$0#][__ort,1639356988.5820549,1639356988.638427,0$0#][__ort,1639356988.6412456,1639356988.6699426,0$0#][__ort,1639356988.6857312,1639356988.6975634,0$0#][__ort,1639356988.7001257,1639356988.7089791,0$0#][__ort,1639356988.7114773,1639356988.720178,0$0#][__ort,1639356988.7223713,1639356988.7311468,0$0#][__ort,1639356988.7333758,1639356988.7421322,0$0#][__ort,1639356988.744172,1639356988.7529004,0$0#][__ort,1639356988.7541926,1639356988.7587526,0$0#][__ort,1639356988.7608337,1639356988.8234704,0$0#][__ort,1639356988.828087,1639356988.9046693,0$0#][__ort,1639356988.9085746,1639356988.9971511,0$0#][__ort,1639356989.001419,1639356989.1028724,0$0#][__ort,1639356989.107679,1639356989.2238061,0$0#][__ort,1639356989.229096,1639356989.3884287,0$0#][__ort,1639356989.3936489,1639356989.5329273,0$0#][__pdf,1639356989.559708,1639356989.5597482,0$0#][__ort,1639356989.9790342,1639356989.9967883,0$0#]]]"""
    tau2 = """t1^time,,0,8,3,1,1e-07,949#{'img_path': '/opt/airflow/workspace/web/dataset/golden/vision_service_document_classification/DIC_Golden_test_set/Others/IMG_1181.jpg', 'overhead_start': 32090, 'overhead': 1360, 'result': '{"pages": [{"detectedDocumentTypes": [{"documentType": "Check", "confidence": 0.9386022686958313}, {"documentType": "Others", "confidence": 0.061126116663217545}, {"documentType": "Taxform", "confidence": 0.00010855369328055531}, {"documentType": "Driver_license", "confidence": 8.459840319119394e-05}, {"documentType": "Passport", "confidence": 7.095218461472541e-05}, {"documentType": "Payslip", "confidence": 3.796189503191272e-06}, {"documentType": "Bank_Statement", "confidence": 2.4644766654091654e-06}, {"documentType": "Receipt", "confidence": 9.99203962237516e-07}, {"documentType": "Resume", "confidence": 1.980021693270828e-07}, {"documentType": "Invoice", "confidence": 1.5690649890487407e-09}]}], "documentClassificationModelVersion": "1.1.12"}'}%n1*[None,inf,inf,0$0#[__predict,1639357002.9975746,1639357004.5263612,0$0#[__ort,1639357003.3147278,1639357003.3159313,0$0#][__ort,1639357003.3573987,1639357003.4807863,0$0#][__ort,1639357003.7179441,1639357003.7609673,0$0#][__ort,1639357003.9064968,1639357003.9187474,0$0#][__ort,1639357003.9219973,1639357004.0949833,0$0#][__pdf,1639357004.1060643,1639357004.106106,0$0#][__ort,1639357004.523819,1639357004.5257595,0$0#]]]"""
    create_gantt_chart_time([tau1, tau2], os.path.join(cur_dir, "data", "tau.png"))

    # test gantt_chart for mem
    mem1 = """t1^get_memory_mb,,0,108,5,0,1e-07,0#%n1*[None,inf,inf,0$0#[__predict,15761.84765625,16704.3671875,0$56#{'start': 1643482387.1305232, 'end': 1643482398.5414443}[__txt,15761.84765625,16704.1015625,0$56#{'start': 1643482387.1662457, 'end': 1643482394.5387013}[__det,15761.84765625,16066.8359375,0$56#{'start': 1643482387.1850543, 'end': 1643482389.8272672}[__ort,15837.8671875,16143.015625,0$56#{'start': 1643482387.2713203, 'end': 1643482389.7219777}]][__rec,16066.8359375,16704.1015625,0$56#{'start': 1643482390.3251693, 'end': 1643482393.7394197}[__ort,16066.8359375,16704.1015625,0$56#{'start': 1643482391.0169199, 'end': 1643482393.1471622}]]][_ort_sess,16704.3515625,16858.96875,0$55#{'start': 1643482395.819777, 'end': 1643482396.1520529}][__tbl,16858.96875,16912.30859375,0$54#{'start': 1643482396.152427, 'end': 1643482396.355825}[__ort,16858.96875,16912.08203125,0$56#{'start': 1643482396.1526206, 'end': 1643482396.3510108}]]]]"""
    mem2 = """t1^get_memory_mb,,0,21,5,0,1e-07,0#%n1*[None,inf,inf,0$0#[__predict,2125.7578125,2125.71875,0$56#{'start': 1643653821.8613808, 'end': 1643653829.5537405}[__txt,2125.7578125,2125.71875,0$55#{'start': 1643653821.9280963, 'end': 1643653827.714213}[__det,2125.7578125,2125.71875,0$55#{'start': 1643653821.963362, 'end': 1643653827.1258452}[__ort,2125.7578125,2125.71875,0$53#{'start': 1643653822.33894, 'end': 1643653827.056082}]]][_ort_sess,2125.71875,2125.7578125,0$56#{'start': 1643653828.9966629, 'end': 1643653829.2985094}]]]"""
    create_gantt_chart_memory([mem1, mem2], os.path.join(cur_dir, "data", "mem.png"))
