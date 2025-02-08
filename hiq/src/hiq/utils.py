# HiQ version 1.1
#
# Copyright (c) 2022, Oracle and/or its affiliates.
# Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
#

import ast
import builtins
import inspect
import io
import itertools
import json
import os
import shutil
import subprocess
import sys
import traceback
from datetime import datetime
from functools import wraps
from time import monotonic, sleep
from typing import Callable, List, Tuple, Union
from types import FunctionType, MethodType


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def __gamma_split(s: str, keep_delim=False, delim="'") -> List[str]:
    results = []
    word = ""
    x = 0
    for c in s:
        if x == 0:
            if c in ("\t", "\n"):
                continue
        if c == delim:
            if x == 0:
                x = 1
                if keep_delim:
                    word += delim
                continue
            elif x == 1:
                if keep_delim:
                    word += delim
                results.append(word)
                word = ""
                x = 0
                continue
        elif c == " ":
            if x == 1:
                pass
            elif x == 0:
                if word:
                    results.append(word)
                    word = ""
                continue
        word += c
    if word:
        results.append(word)
    return results


def execute_cmd(
    command: str,
    split=True,
    verbose=True,
    check=False,
    shell=False,
    timeout=600,
    stderr_log=None,
    debug=False,
    keep_delim=False,
    env=None,
    error_file=None,
    append_error=False,
    runtime_output=False,
) -> Union[str, List[str], int]:
    """
    If verbose is true, print out input.
    If check is true, and the process exits with a non-zero exit code, a CalledProcessError exception will be raised.
    Attributes of that exception hold the arguments, the exit code, and stdout and stderr if they were captured.
    stderr_log could be: stderr_log=open("gamma.error.log", "a+")
    https://docs.python.org/3/library/subprocess.html#subprocess.run
    """
    error_file = error_file or f".error.{random_str()}.log"
    if stderr_log is None:
        stderr_log = open(error_file, "w", encoding="utf8")
    try:
        commands = __gamma_split(command, keep_delim, delim='"')
        commands = [i.replace('"','') for i in commands]
        cmd = " ".join(commands)
        if verbose:
            print(f"🏃‍♂️ command: {cmd}, error_file: {error_file}")
        start = monotonic()
        if runtime_output:
            ret = 0
            if timeout>0:
                proc = subprocess.Popen(
                    cmd,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env if env else {},
                )
                # Loop over the subprocess output and print it immediately
                while True:
                    output = proc.stdout.readline().decode().rstrip()
                    if output == "" and proc.poll() is not None:
                        break
                    sleep(0.2)
                    if monotonic() - start > timeout:
                        print(f"Command timeout after {timeout} seconds. command: {cmd}")
                        break
                    print(output)
                ret = proc.wait()
                return ret
            else:
                subprocess.run(commands)
                return ret
        elif env is None:
            result = subprocess.run(
                commands,
                stdout=subprocess.PIPE,
                stderr=stderr_log,
                check=check,
                shell=shell,
                timeout=timeout,
            )
        else:
            result = subprocess.run(
                commands,
                stdout=subprocess.PIPE,
                stderr=stderr_log,
                check=check,
                shell=shell,
                timeout=timeout,
                env=env,
            )
        if os.path.exists(error_file) and os.path.getsize(error_file) and debug:
            print("☠️ error:", read_file(error_file, binary_mode=True, by_line=False))
        if split:
            ret = result.stdout.decode("utf-8").strip().split("\n")
        else:
            ret = result.stdout.decode("utf-8").strip()
        if (
            append_error
            and os.path.exists(error_file)
            and os.path.getsize(error_file) > 0
        ):
            if isinstance(ret, str):
                ret += read_file(error_file, by_line=False)
            else:
                ret.append(read_file(error_file, by_line=False))
        return ret
    except subprocess.TimeoutExpired:
        print(f"🏃‍♂️ command timed-out after {timeout} seconds: {command}")
    finally:
        if stderr_log and hasattr(stderr_log, "close"):  # don't want to import io :-)
            stderr_log.close()
        if os.path.exists(error_file) and not debug:
            if os.path.getsize(error_file) == 0:
                os.unlink(error_file)
                if verbose:
                    print(f"{error_file} is empty and removed")
            elif verbose:
                print("*" * 80)
                print(read_file(error_file, by_line=False))
                print("*" * 80)


def utc_to_pst(utc: str, format_="%Y-%m-%dT%H:%M:%S+0000") -> str:
    """utc2pst("2021-06-19T20:32:18+0000")"""
    from dateutil import tz

    from_zone = tz.gettz("UTC")
    to_zone = tz.gettz("America/Los_Angeles")
    utc = datetime.strptime(utc, format_)
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return str(central)


def ts_to_dt(timestamp: float) -> str:
    if timestamp < 1633279464 // 2:
        # print(f"warning: {timestamp} is not a timestamp")
        return str(timestamp)
    try:
        dt_object = datetime.fromtimestamp(timestamp)
        return dt_object.strftime(r"%Y-%m-%d %H:%M:%S.%f")
    except OverflowError as e:
        print(f"error: timestamp {timestamp} cased overflow")
        return ""


def ts_pair_to_dt(t1: float, t2: float) -> str:
    d1 = datetime.fromtimestamp(t1)
    s1 = d1.strftime(r"%Y-%m-%d %H:%M:%S.%f")
    p1 = s1.split(" ")
    d2 = datetime.fromtimestamp(t2)
    s2 = d2.strftime(r"%Y-%m-%d %H:%M:%S.%f")
    p2 = s2.split(" ")
    if p1[0] == p2[0]:
        return f"{p1[0]} {p1[1]} - {p2[1]}"
    return f"{s1} - {s2}"


def get_time_by_time_zone(time_zone="US/Pacific") -> datetime:
    import pytz

    return datetime.now(tz=pytz.utc).astimezone(pytz.timezone(time_zone))


def get_time_str_with_tz(time_zone="US/Pacific") -> str:
    import pytz

    date_format = "%Y-%m-%d %H:%M:%S.%Z"
    date = datetime.now(tz=pytz.utc)
    date = date.astimezone(pytz.timezone(time_zone))
    pst_datetime = date.strftime(date_format)
    return pst_datetime


def parse_lambda(l):
    try:
        c = inspect.getsource(l).lstrip()
        source_ast = ast.parse(c)
        n = next(
            (node for node in ast.walk(source_ast) if isinstance(node, ast.Lambda)),
            None,
        )
        if n.end_lineno == n.lineno and n.lineno == 1:
            return c[n.col_offset : n.end_col_offset]
        else:
            r = []
            start = False
            s = c.split("\n")
            for i, v in enumerate(s):
                if start:
                    if n.end_lineno == i + 1:
                        r.append(s[i][: n.end_col_offset])
                        break
                    else:
                        r.append(v)
                elif n.lineno == i + 1:
                    r.append(s[i][n.col_offset :])
                    start = True
            return "\n".join(r)
    except OSError:
        return None


def _get_full_argspecs(x) -> Tuple[str, str]:
    try:
        return _get_args_spec(inspect.getfullargspec(inspect.unwrap(x)))
    except TypeError:
        import re

        docstring = x.__doc__
        match = re.search(r"\(([^)]*)\)", docstring)
        signature_with_default = str(match.group(1)).replace(", ", ",")
        signature_without_default = re.sub(r"=[^,]+", "", signature_with_default)
        return signature_with_default, signature_without_default


def _get_args_spec(args_spec) -> Tuple[str, str]:
    x = args_spec.args
    varkw = args_spec.varkw
    if args_spec.defaults is None:
        if varkw:
            x.append(f"**{varkw}")
        return ",".join(x), ",".join(x)
    y = list(args_spec.defaults)
    y = ["^"] * (len(x) - len(y)) + y
    z = list(zip(x, y))
    r = list(
        map(
            lambda e: e[0]
            if e[1] == "^"
            else (
                f"{e[0]}='{e[1]}'"
                if isinstance(e[1], str)
                else f"{e[0]}={parse_lambda(e[1])}"
                if "<function <lambda> at" in str(e[1])
                else f"{e[0]}={e[1]}"
            ),
            z,
        )
    )
    if varkw:
        r.append(f"**{varkw}")
        x.append(f"**{varkw}")
    return ",".join(r), ",".join(x)


# File System related


def read_file(
    file_path: str,
    binary_mode: bool = False,
    by_line: bool = True,
    filter_func: Callable = None,
    as_json=False,
    bytes_as_string=True,
    raise_=False,
    strip=False,
) -> Union[List[str], bytes]:
    """A handy function to read file

    Args:
        file_path (str): file path
        raise_ (bool): populate exception when it happens, for instance, when it's False, in case the file doesn't exist, return None
        strip (bool): strip the string output or not?

    Don't use this for super large file.

    Examples:

    .. highlight:: python
    .. code-block:: python

        >>> from pprint import pprint as pp
        >>> here = os.path.dirname(os.path.realpath(__file__))
        >>> data = read_file(f"{here}/o.json")
        >>> pp(data)
        ['{',
        '    "eventKey": "repo:refs_changed",',
        '    "date": "2021-09-21T04:52:51+0000",',
        '    "actor": {',
        '        "name": "fuhengwu",',
        '        "emailAddress": "fuheng.wu@oracle.com",',
        '        "id": 937189,',
        '        "displayName": "fuheng wu",',
        '        "active": true,',
        '        "slug": "fuhengwu",',
        '        "type": "NORMAL",',
        '        "links": {',
        '            "self": [{ "href": '
        '"https://www.github.com/users/fuhengwu" }]',
        '        }',
        '    }',
        '}']
        >>> data = read_file(f"{here}/o.json", binary_mode=True)
        >>> pp(data)
        (b'{\\n    "eventKey": "repo:refs_changed",\\n    "date": "2021-09-21T04:52:51+'
        b'0000",\\n    "actor": {\\n        "name": "fuhengwu",\\n        "emailAddress":'
        b' "fuheng.wu@oracle.com",\\n        "id": 937189,\\n        "displayName": "F'
        b'uheng Wu",\\n        "active": true,\\n        "slug": "fuhengwu",\\n        "t'
        b'ype": "NORMAL",\\n        "links": {\\n            "self": [{ "href": "https'
        b'://www.github.com/users/fuhengwu" }]\\n        }\\n    }\\n}')
        >>> data = read_file(f"{here}/o.json", as_json=True)
        >>> pp(data)
        {'actor': {'active': True,
                'displayName': 'fuheng wu',
                'emailAddress': 'fuheng.wu@oracle.com',
                'id': 937189,
                'links': {'self': [{'href': 'https://www.github.com/users/fuhengwu'}]},
                'name': 'fuhengwu',
                'slug': 'fuhengwu',
                'type': 'NORMAL'},
        'date': '2021-09-21T04:52:51+0000',
        'eventKey': 'repo:refs_changed'}
    """
    if not os.path.isfile(file_path):
        if not raise_:
            return None
        raise ValueError(f"input path {file_path} is not a file")
    # assert by_line != as_json, "Can not read file by line with as_json"
    if as_json:  # give as_json higher priority
        by_line = False
    res = b"" if binary_mode else []
    with open(file_path, "rb" if binary_mode else "r") as file:
        if binary_mode:
            res = file.read()
        else:
            res = file.read()
            if by_line:
                res = res.splitlines()
                if filter_func:
                    res = list(filter(filter_func, res))
    if as_json:
        res = json.loads(res)
    if not binary_mode and isinstance(res, (bytes,)) and bytes_as_string:
        res = res.decode("utf-8")
    if isinstance(res, str) and strip:
        return res.strip()
    return res


def write_file(file_path, data, as_owner=None, as_group=None, append=False, mod_="644"):
    """write data into file. if file_path is just a file name, the file will be created in current directory"""
    if os.path.exists(file_path) and as_owner:
        execute_cmd(f"sudo chown {as_owner} {file_path}", timeout=10, debug=True)
    if "/" in file_path:
        ensure_folder(file_path)
    if append:
        execute_cmd(f"touch {file_path}")
    with open(file_path, "ab" if append else "wb") as file:
        if isinstance(data, bytes):
            file.write(data)
        else:
            file.write(data.encode("utf-8"))
        if as_owner:
            execute_cmd(f"sudo chown {as_owner} {file_path}", timeout=10, debug=True)
        if as_group:
            execute_cmd(f"sudo chgrp {as_group} {file_path}", timeout=10, debug=True)
        if mod_ != "644":
            execute_cmd(f"chmod {mod_} {file_path}", timeout=10, debug=True)


def ensure_folder(path_str: str):
    """ensure there is a folder for the path_str, the input is supposed to be a FILE path"""
    try:
        if not os.path.isdir(path_str):
            path_str = os.path.dirname(path_str)
        if path_str and not os.path.exists(path_str):
            os.makedirs(path_str)
        return path_str
    except PermissionError as e:
        print(f"🦉 Warning: you have no permission to access path: {path_str}")
        raise e


def download_from_http(
    uri, local_file_path, display=False, enable_proxy=True, auth=None
) -> str:
    """auth=(user, password)"""
    import requests
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    try:
        proxies = {}
        if enable_proxy:
            proxies = get_proxies()
        if not (auth is None or (isinstance(auth, (tuple, list)) and len(auth) == 2)):
            raise ValueError(f"auth information is wrong: {auth}")
        response = requests.get(
            uri, verify=False, stream=True, proxies=proxies, auth=auth
        )
        if response.status_code >= 400:
            raise IOError(
                response.status_code,
                f"Error retrieving {uri}. {response.status_code}: {response.text}",
            )
        total_size_in_bytes = int(response.headers.get("content-length", 0))
        if not display:
            response.raw.decode_content = True
            with open(local_file_path, "wb") as f:
                shutil.copyfileobj(response.raw, f)
        else:
            from tqdm import tqdm

            if total_size_in_bytes > 0:
                block_size = 1024 * 500  # 500 KiB
                with tqdm(
                    total=total_size_in_bytes, unit="iB", unit_scale=True
                ) as progress_bar:
                    file_obj = io.BytesIO()
                    for data in response.iter_content(block_size):
                        progress_bar.update(len(data))
                        file_obj.write(data)
                if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                    raise ValueError(
                        f"💀 error happens when downloading {uri} to {local_file_path}"
                    )
            if total_size_in_bytes <= 0:
                response = requests.get(uri, verify=False)
                file_obj = io.BytesIO()
                file_obj.write(response.content)
            file_obj.seek(0, 0)
            with open(local_file_path, "wb") as out:
                out.write(file_obj.read())
        return local_file_path
    except Exception as e:
        print(f"🦉 error: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        raise e


def random_str(length_of_string=12):
    import random
    import string

    letters_and_digits = string.ascii_lowercase + string.digits
    random_string = ""
    for _ in range(length_of_string):
        random_string += random.choice(letters_and_digits)
    return random_string


def random_port(start_port=1024, end_port=65535):
    """
    Returns a random port number within the specified range.

    :param start_port: The starting port number of the range (inclusive).
    :param end_port: The ending port number of the range (inclusive).
    :return: A random port number within the specified range.
    """
    import random
    if not (1024 <= start_port <= 65535 and 1024 <= end_port <= 65535):
        raise ValueError("Port numbers must be in the range 1024-65535")
    if start_port > end_port:
        raise ValueError("start_port must be less than or equal to end_port")

    return random.randint(start_port, end_port)

class SilencePrint(object):
    def __enter__(self):
        self.old_print = builtins.print
        builtins.print = lambda *args, **kwargs: None

    def __exit__(self, exc_type, exc_value, exc_tb):
        builtins.print = self.old_print


def get_proxies() -> dict:
    proxies = {
        "http": os.environ.get("http_proxy", ""),
        "https": os.environ.get("https_proxy", ""),
        "ftp": os.environ.get("ftp_proxy", ""),
        "no_proxy": os.environ.get("no_proxy", ""),
    }
    return proxies


def _check_overhead(f, *args, **kwargs):
    @wraps(f)
    def __y(s, *args, **kwargs):
        start = monotonic()
        r = f(s, *args, **kwargs)
        s.check_oh_counter += 1
        s.overhead_us += int((monotonic() - start) * 1e6)
        return r

    return __y


def get_env_bool(x, default=None) -> bool:
    """Get bool type environment variable

    These values will be treated as True:

        non-empty string, non-zero numeric


    >>> import os
    >>> from hiq.utils import get_env_bool
    >>> get_env_bool('hello')
    False
    >>> os.environ["hello"]=""
    >>> get_env_bool('hello')
    False
    >>> os.environ["hello"]="1"
    >>> get_env_bool('hello')
    True
    >>> os.environ["hello"]="0"
    >>> get_env_bool('hello')
    False
    >>> os.environ["hello"]="true"
    >>> get_env_bool('hello')
    True

    """
    t = os.environ.get(x, default)
    if isinstance(t, str) and t:
        try:
            return bool(ast.literal_eval(t))
        except:
            return True
    return bool(t)


def get_env_int(x, default=0) -> int:
    return int(os.environ.get(x, default))


def get_env_float(x, default=0) -> float:
    return float(os.environ.get(x, default))


def is_hiqed(fun: Callable, fun_name: str) -> bool:
    """check if this function has been registered in HiQ system

    The function could be one of:

        full_qualified_name="<method 'read' of '_io.TextIOWrapper' objects>", fun_name='read'

        full_qualified_name='<function main at 0x7f7f2eaf6040>', fun_name='main'

        full_qualified_name='<built-in function read>', fun_name='read'

        full_qualified_name="<bound method BaseModel.from_pretrained of <class ..." (static class method)

    Args:
        fun (Callable): original function
        fun_name (str): function name

    Returns:
        bool: is this function has been registered in HiQ
    """
    full_qualified_name = str(fun)
    # print(f"🐵 {full_qualified_name=}, {fun_name=}")
    return (
        f"{fun_name} at" not in full_qualified_name
        and f"<method '{fun_name}' of" not in full_qualified_name
        and not full_qualified_name.startswith("<built-in function")
        and not full_qualified_name.startswith("<bound method")
    )


def lmk_data_handler(data: dict = {}, pid=os.getpid()) -> str:
    """convert raw data of Log Monkey King to the format we want to log

    Args:
        data (dict, optional): a data dictionary. If not empty, the keys should be: `id_`, `name`, `value`, `extra`, `is_start`. Defaults to {}.
        pid ([type], optional): LMK process id. Defaults to os.getpid().

    Returns:
        str: a log entry as a data string
    """
    id_ = data["id_"]
    name = data["name"][2:]
    value = data["value"]
    extra = data["extra"]
    is_start = data["is_start"]

    monkey = "🐵" if is_start else "🙈"
    if "time" in extra:
        data = f"{ts_to_dt(extra['time'])} - [{id_}] [🆔 {pid}] {monkey} [{name}] {value} {extra}"
    else:
        if extra:
            data = f"{ts_to_dt(value)} - [{id_}] [🆔 {pid}] {monkey} [{name}] {extra}"
        else:
            data = f"{ts_to_dt(value)} - [{id_}] [🆔 {pid}] {monkey} [{name}]"
    return data


def get_home():
    from pathlib import Path

    return str(Path.home())


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonBase(metaclass=SingletonMeta):
    pass


def memoize(func):
    cache = dict()

    def __x(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result

    return __x


def memoize_first(func):
    cache = dict()

    def __x(*args):
        if args[0] in cache:
            return cache[args[0]]
        result = func(*args)
        cache[args[0]] = result
        return result

    return __x


def get_cpu_info(debug=False):
    cpuset = os.sched_getaffinity(0)
    if debug:
        print(f"{len(os.sched_getaffinity(0))} CPUs are available: {cpuset}")
    return cpuset


def pretty_time_delta(seconds):
    sign_string = "-" if seconds < 0 else ""
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return "%s%dd%dh%dm%ds" % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return "%s%dh%dm%ds" % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return "%s%dm%ds" % (sign_string, minutes, seconds)
    else:
        return "%s%ds" % (sign_string, seconds)


def create_gantt_chart_time(
    data: List[str], fig_path=None, return_as_stream=False, fig_size=(24, 24)
):
    """Plot Gantt-chart for HiQ Latency Tree"""
    from hiq import tree
    import pandas as pd
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    import numpy as np
    import random

    if isinstance(data, str):
        data = [data]

    # Return DataFrame of Data
    def create_df(data):
        # Traverse tree to get name and time-stamps
        def dfs(result, pass_name, num, node):
            if pass_name == "":
                if node.start == float("inf"):
                    # start time
                    s = ""
                    # end time
                    e = ""
                else:
                    # start time
                    s = datetime.fromtimestamp(float(node.start))
                    # end time
                    e = datetime.fromtimestamp(float(node.end))
                result.append(
                    [
                        str(pass_name) + str(node.name.strip("_")) + "." + str(num),
                        str(node.name.strip("_")),
                        s,
                        e,
                    ]
                )
            else:
                if node.start == float("inf"):
                    # start time
                    s = ""
                    # end time
                    e = ""
                else:
                    # start time
                    s = datetime.fromtimestamp(float(node.start))
                    # end time
                    e = datetime.fromtimestamp(float(node.end))
                result.append(
                    [
                        str(pass_name)
                        + "."
                        + str(node.name.strip("_"))
                        + "."
                        + str(num),
                        str(node.name.strip("_")),
                        s,
                        e,
                    ]
                )
            if node.nodes:
                for nd in node.nodes:
                    num += 1
                    if str(node.name) == "None":
                        pn = str(pass_name)
                    else:
                        if pass_name == "":
                            pn = str(pass_name) + str(node.name.strip("_"))
                        else:
                            pn = str(pass_name) + "." + str(node.name.strip("_"))
                    result = dfs(result, pn, num, nd)
                return result
            else:
                return result

        all_result = []
        total_data = len(data)
        for i in range(total_data):
            # Create tree
            t = tree.Tree(data[i])
            # Extract data from Tree
            pass_name = "Call-" + str(i + 1)
            dfs_result = []
            dfs_result = dfs(dfs_result, pass_name, 0, t.root)
            dfs_result = dfs_result[1:]

            req = []
            req.append(pass_name)
            req.append("Requests")
            req_start = min([s[2] for s in dfs_result])
            req_end = max([e[3] for e in dfs_result])
            req.append(req_start)
            req.append(req_end)
            dfs_result.append(req)

            all_result.append(dfs_result)

        # Generate random Hex color code
        def get_color():
            hex_number = [
                "#" + "".join([random.choice("ABCDEF0123456789") for i in range(6)])
            ]
            return hex_number[0]

        # Create dfs
        def create_dfs_from_list(req_result):
            df = pd.DataFrame(req_result, columns=["Name", "Group", "Start", "End"])

            proj_start = df.Start.min()

            # Difference is in seconds
            df["start_num"] = (df.Start - proj_start).dt.total_seconds()

            df["end_num"] = (df.End - proj_start).dt.total_seconds()

            df["time_start_to_end"] = df.end_num - df.start_num

            c_dict = {}
            for i in df["Group"].unique():
                c_dict[i] = get_color()

            # Attach color to the group
            def color(row, cc_dict=c_dict):
                return cc_dict[row["Group"]]

            df["color"] = df.apply(color, axis=1)

            return [df, c_dict, proj_start]

        all_dfs = []
        for r in all_result:
            all_dfs.append(create_dfs_from_list(r))

        return all_dfs

    all_dfs = create_df(data)

    #### Create Plots ####
    fl = len(all_dfs)
    fig, ax_plots = plt.subplots(1, fl, figsize=(fl * fig_size[0], fig_size[1]))

    for i in range(fl):
        if fl == 1:
            ax = ax_plots
        else:
            ax = ax_plots[i]
        df = all_dfs[i][0]
        c_dict = all_dfs[i][1]
        proj_start = all_dfs[i][2]

        ax.barh(df.Name, df.time_start_to_end, left=df.start_num, color=df.color)

        legend_elements = [
            Patch(facecolor=c_dict[i], label=i.strip("_")) for i in c_dict
        ]
        ax.legend(handles=legend_elements)

        number_of_vertical_lines = 14
        interval = (df.end_num.max() + 1) / number_of_vertical_lines
        xticks = np.arange(0, df.end_num.max() + 1, interval)
        xticks_labels = (
            pd.date_range(proj_start, end=df.End.max(), periods=len(xticks))
            .floor("ms")
            .format(".%3f")[1:]
        )
        xticks_minor = np.arange(0, df.end_num.max() + 1, 1)

        ax.tick_params(rotation=80, axis="x")
        ax.set_xticks(xticks)
        ax.set_xticks(xticks_minor, minor=True)
        ax.set_xticklabels(xticks_labels[::1])
        ax.title.set_text("Call-" + str(i + 1))
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Function")
        ax.grid()

    fig.tight_layout()
    if return_as_stream:
        buf = io.BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        return buf.read()
    if fig_path is None:
        fig_path = f"hiq.tim_{random_str()}.png"
    ensure_folder(fig_path)
    plt.savefig(fig_path)
    if os.path.exists(fig_path):
        return fig_path
    print("could not save file")
    return None


def create_gantt_chart_memory(data: List[str], fig_path=None):
    """Plot Gantt-chart for HiQ Memory Tree"""
    from hiq import tree
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np
    import random
    from matplotlib.patches import Patch

    if isinstance(data, str):
        data = [data]

    # Return DataFrame of Data
    def create_df(data):
        # Traverse tree to get name and time-stamps
        def dfs(result, pass_name, num, node, r_min, r_max):
            if pass_name == "":
                if node.name == "None":
                    s, e, m = "", "", ""
                else:
                    if node.extra["start"] == float("inf"):
                        s, e, m = "", "", ""
                    else:
                        s = datetime.fromtimestamp(float(node.extra["start"]))
                        e = datetime.fromtimestamp(float(node.extra["end"]))
                        m = float(node.end) - float(node.start)
                        r_min = min(r_min, float(node.start))
                        r_max = max(r_max, float(node.end))
                result.append(
                    [
                        str(pass_name) + str(node.name.strip("_")) + "." + str(num),
                        str(node.name.strip("_")),
                        s,
                        e,
                        m,
                    ]
                )
            else:
                if node.name == "None":
                    s, e, m = "", "", ""
                else:
                    if node.extra["start"] == float("inf"):
                        s, e, m = "", "", ""
                    else:
                        s = datetime.fromtimestamp(float(node.extra["start"]))
                        e = datetime.fromtimestamp(float(node.extra["end"]))
                        m = float(node.end) - float(node.start)
                        r_min = min(r_min, float(node.start))
                        r_max = max(r_max, float(node.end))
                result.append(
                    [
                        str(pass_name)
                        + "."
                        + str(node.name.strip("_"))
                        + "."
                        + str(num),
                        str(node.name.strip("_")),
                        s,
                        e,
                        m,
                    ]
                )
            if node.nodes:
                for nd in node.nodes:
                    num += 1
                    if str(node.name) == "None":
                        pn = str(pass_name)
                    else:
                        if pass_name == "":
                            pn = str(pass_name) + str(node.name.strip("_"))
                        else:
                            pn = str(pass_name) + "." + str(node.name.strip("_"))
                    result, r_min, r_max = dfs(result, pn, num, nd, r_min, r_max)
                return result, r_min, r_max
            else:
                return result, r_min, r_max

        all_result = []
        total_data = len(data)
        for i in range(total_data):
            # Create tree
            t = tree.Tree(data[i])
            # Extract data from Tree
            pass_name = "Call-" + str(i + 1)
            dfs_result = []
            dfs_result, r_min, r_max = dfs(
                dfs_result, pass_name, 0, t.root, float("inf"), 0
            )
            dfs_result = dfs_result[1:]

            req = []
            req.append(pass_name)
            req.append("Requests")
            req_start = min([s[2] for s in dfs_result])
            req_end = max([e[3] for e in dfs_result])
            req_memory = r_max - r_min
            req.append(req_start)
            req.append(req_end)
            req.append(req_memory)
            dfs_result.append(req)

            all_result.append(dfs_result)

        # Generate random Hex color code
        def get_color():
            hex_number = [
                "#" + "".join([random.choice("ABCDEF0123456789") for i in range(6)])
            ]
            return hex_number[0]

        # Create dfs
        def create_dfs_from_list(req_result):
            df = pd.DataFrame(
                req_result, columns=["Name", "Group", "Start", "End", "Memory"]
            )
            proj_start = df.Start.min()
            # Difference is in seconds
            df["start_num"] = (df.Start - proj_start).dt.total_seconds()
            df["end_num"] = (df.End - proj_start).dt.total_seconds()
            df["time_start_to_end"] = df.end_num - df.start_num
            c_dict = {}
            for i in df["Group"].unique():
                c_dict[i] = get_color()

            # Attach color to the group
            def color(row, cc_dict=c_dict):
                return cc_dict[row["Group"]]

            df["color"] = df.apply(color, axis=1)
            return [df, c_dict, proj_start]

        all_dfs = []
        for r in all_result:
            all_dfs.append(create_dfs_from_list(r))
        return all_dfs

    all_dfs = create_df(data)

    #### Create Plots ####
    fl = len(all_dfs)
    fig, ax_plots = plt.subplots(1, fl, figsize=(fl * 10, 7))

    for i in range(fl):
        if fl == 1:
            ax = ax_plots
        else:
            ax = ax_plots[i]
        df = all_dfs[i][0]
        c_dict = all_dfs[i][1]
        proj_start = all_dfs[i][2]

        ax.barh(df.Name, df.time_start_to_end, left=df.start_num, color=df.color)
        # Display memory
        for idx, row in df.iterrows():
            ax.text(
                row.end_num + 0.1,
                idx,
                format(float(row.Memory), ".3f"),
                va="center",
                alpha=0.8,
            )
        legend_elements = [
            Patch(facecolor=c_dict[i], label=i.strip("_")) for i in c_dict
        ]
        ax.legend(handles=legend_elements)

        number_of_vertical_lines = 14
        interval = (df.end_num.max() + 1) / number_of_vertical_lines
        xticks = np.arange(0, df.end_num.max() + 1, interval)
        xticks_labels = (
            pd.date_range(proj_start, end=df.End.max(), periods=len(xticks))
            .floor("ms")
            .format(".%3f")[1:]
        )
        xticks_minor = np.arange(0, df.end_num.max() + 1, 1)

        ax.tick_params(rotation=80, axis="x")
        ax.set_xticks(xticks)
        ax.set_xticks(xticks_minor, minor=True)
        ax.set_xticklabels(xticks_labels[::1])
        ax.title.set_text("Call-" + str(i + 1))
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Function")
        ax.grid()

    fig.tight_layout()
    if fig_path is None:
        fig_path = f"hiq.mem_{random_str()}.png"
    ensure_folder(fig_path)
    plt.savefig(fig_path)
    if os.path.exists(fig_path):
        return fig_path


def down_sample(a_list: list, k: int, debug=False):
    import numpy as np

    if len(a_list) < k:
        print("💀" * 80)
        print(
            f"🦉 warning: k={k} is too big for a length-{len(a_list)} list in downsampling, return original list"
        )
        return a_list
    idx = list(map(int, list(np.linspace(0, len(a_list) - 1, k, endpoint=True))))
    if debug:
        print(
            f"👻 original list size: {len(a_list)}, new list size:{len(idx)}, idx: {idx}"
        )
    return [a_list[i] for i in idx]


DEFAULT_IMG_TYPES = ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.tiff"]
ALL_IMG_DOC_TYPES = DEFAULT_IMG_TYPES + ["*.webp", "*.pdf"]


def get_files_by_type(
    folder_path=os.getcwd(),
    types=ALL_IMG_DOC_TYPES,
    include_folder_name=False,
    sorting=True,
    sort_by=0,
    ascending=True,
    sample_num=None,
    topk=None,
    recursive=True,
    verbose=True,
) -> list:
    """Get file dataset as a list of (fsize, file, file_name )

    ```
    for fsize, image_name, image_file in image_files:
        ...
    ```
    Args:
        folder_path (str, optional): [description]. Defaults to "img".
        types (tuple, optional): [description]. Defaults to ALL_IMG_DOC_TYPES.

    Returns:
        List[Tuple(str)]: a list of file information tuple
    """
    import glob
    
    if isinstance(types, str):
        types = [types]

    files_grabbed = []
    for ts in types:
        for t in map("".join, itertools.product(*zip(ts.upper(), ts.lower()))):
            files_grabbed.extend(
                glob.glob(f"{folder_path}/**/{t}", recursive=recursive)
            )

    res = []
    for file_path in set(files_grabbed):
        file_size = os.path.getsize(file_path)
        tmp = file_path.split("/")
        if len(tmp) < 2:
            raise ValueError(f"file path is too short: {file_path}")
        file_name = tmp[-1]
        folder_name = tmp[-2] if len(tmp) > 2 else None
        if include_folder_name:
            res.append((file_size, file_name, file_path, folder_name))
        else:
            res.append((file_size, file_name, file_path))
    if sorting:
        res = sorted(res, reverse=not ascending, key=lambda x: x[sort_by])
    if len(res) > 2 and verbose:
        print(f"🦶 res[0]:{res[0]}, res[-1]:{res[-1]}")
    if topk:
        return res[:topk]
    if sample_num:
        return down_sample(res, sample_num)
    if len(res) > 1000 and verbose:
        print(f"😱 big number of files: {len(res)}")
    return res


HEADERS = {"client-id": "hiq-client", "Content-Type": "application/json"}


def __send_http(
    url,
    data,
    auth=None,
    headers=HEADERS,
    timeout=60,
    trust_env=True,
    enable_proxy=True,
    method="get",
):
    try:
        import requests

        session = requests.Session()
        session.trust_env = trust_env
        if isinstance(data, dict):
            data = json.dumps(data)
        payload = {"data": data, "headers": headers, "timeout": timeout}
        if auth:
            payload["auth"] = auth
        proxies = get_proxies() if enable_proxy else dict()
        resp = getattr(session, method)(url, proxies=proxies, **payload)
        return resp
    except Exception as e:
        print(f"🦉 error: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        raise e


def post_http(
    url,
    data,
    auth=None,
    headers=HEADERS,
    timeout=60,
    trust_env=True,
    enable_proxy=True,
):
    return __send_http(
        url, data, auth, headers, timeout, trust_env, enable_proxy, method="post"
    )


def get_average_loss(a, b):
    import numpy as np

    if isinstance(a, list):
        r = 0.0
        for i in range(len(a)):
            r += get_average_loss(a[i], b[i])
            return r
    delta = np.abs(a - b)
    return np.average(delta)


def get_percentage_loss(a, b):
    import numpy as np

    if isinstance(a, list):
        r = 0.0
        for i in range(len(a)):
            r += get_percentage_loss(a[i], b[i])
            return r
    delta = np.abs(a - b)
    return np.abs(np.sum(delta) / np.sum(a))


def bfloat16_supported(device_type="cuda"):
    import torch

    try:
        with torch.amp.autocast(device_type=device_type, dtype=torch.bfloat16):
            return True
    except:
        return False


def __extract_wrapped(decorated):
    if decorated.__closure__ is None:
        return None
    closure = (c.cell_contents for c in decorated.__closure__)
    return next((c for c in closure if isinstance(c, FunctionType)), None)


def signature(obj, *, follow_wrapped=True):
    if not isinstance(obj, MethodType):
        return inspect.Signature.from_callable(obj, follow_wrapped=follow_wrapped)
    z_arg = __extract_wrapped(obj)
    z = (
        None
        if z_arg is None
        else inspect.Signature.from_callable(z_arg, follow_wrapped=follow_wrapped)
    )
    return (
        inspect.Signature.from_callable(
            inspect.unwrap(obj), follow_wrapped=follow_wrapped
        )
        if z is None
        else z
    )

def draw_image(image_np, format='CHW', normalize=True, save=True, axis='on', folder="hiq_vis", prefix=""):
    """image_np is a numpy array with CHW format"""
    import matplotlib.pyplot as plt
    import numpy as np
    import hiq
    import time
    
    if not isinstance(image_np, np.ndarray):
        image_np = image_np.numpy()
    if len(image_np.shape) == 4:
        image_np = image_np[0]
    cmap = None
    if format == "CHW":
        # CHW => HWC
        image_np = np.transpose(image_np, (1, 2, 0))
        if image_np.shape[2] > 3:
            image_np = image_np[:, :, 0]
            cmap = "gray"
    if normalize:
        image_np = (image_np - image_np.min()) / (image_np.max() - image_np.min())
    if cmap is None:
        plt.imshow(image_np)
    else:
        plt.imshow(image_np, cmap=cmap)
    plt.axis(axis)
    if save:
        if prefix!="" and not prefix.endswith("_"):
            prefix += "_"
        img_path = f"{folder}/{prefix}{int(time.time())}_{hiq.random_str()}.png"
        ensure_folder(img_path)
        plt.savefig(img_path, bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()
    else:
        plt.show(block=True)

def set_seed(seed=42, has_tf=False, has_torch=False, has_jax=False, has_pl=False):
    import random
    random.seed(seed)
    try:
        import numpy as np
        np.random.seed(seed)
    except ImportError as e:
        pass

    if has_jax:
      try:
          import jax
          jax.random.PRNGKey(seed)
      except ImportError as e:
          pass

    if has_tf:
        try:
            import tensorflow as tf
            tf.random.set_seed(seed)
        except ImportError as e:
            pass

    if has_pl:
        try:
            import pytorch_lightning as pl
            pl.seed_everything(seed)
        except ImportError as e:
            pass

    if has_torch:
        try:
            import torch
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(seed)
                torch.cuda.manual_seed_all(seed)
                torch.backends.cudnn.enable = False
                torch.backends.cudnn.benchmark = False
                torch.backends.cudnn.deterministic = True
        except ImportError as e:
            pass


def str_to_filename(s, repl='_', suffix=None):
    import re
    s = re.sub(r'[^a-zA-Z0-9]', repl, s)
    s = re.sub(r'__+', repl, s)
    s = s.strip(repl)
    if not s:
        s = random_str()
    if suffix is not None:
        s = s + "." + suffix
    return s

if __name__ == "__main__":
    import requests

    print(total_gpu_memory_mb())

    print(pretty_time_delta(730.2312341))
    args = _get_args_spec(inspect.getfullargspec(requests.get))
    print(args)
    data = read_file(f"{get_home()}/.bashrc", by_line=False, binary_mode=False)
    print(data)

    mtree = """t1^get_memory_mb,,0,108,5,0,1e-07,0#%n1*[None,inf,inf,0$0#[__predict,2146.82421875,2146.37890625,0$55#{'start': 1643569736.1171584, 'end': 1643569747.438287}[__txt,2146.82421875,2146.12890625,0$56#{'start': 1643569736.1535447, 'end': 1643569744.0208213}[__det,2146.82421875,2146.546875,0$55#{'start': 1643569736.2086039, 'end': 1643569738.931958}[__ort,2146.82421875,2146.546875,0$56#{'start': 1643569736.3555777, 'end': 1643569738.8348844}]][__rec,2146.546875,2146.12890625,0$55#{'start': 1643569739.5116146, 'end': 1643569743.115841}[__ort,2146.546875,2146.12890625,0$56#{'start': 1643569740.1161213, 'end': 1643569742.6137362}]]][_ort_sess,2146.37890625,2146.41796875,0$54#{'start': 1643569745.352344, 'end': 1643569745.630854}]]]"""
    print(create_gantt_chart_memory([mtree]))

    tau = """t1^time,,0,108,5,1,1e-07,47#{'overhead_start': 14461965, 'overhead': 39488}%n1*[None,inf,inf,0$0#[__predict,1643569736.1171172,1643569747.4377651,0$29#{'start': 1643569736.1171584}[__pdf,1643569736.1183336,1643569736.1530828,0$0#][__txt,1643569736.1535318,1643569744.0208154,0$0#[__sdc,1643569736.1536727,1643569736.16426,0$0#[__ort,1643569736.160469,1643569736.1639962,0$0#]][__res,1643569736.1644254,1643569736.2080786,0$0#[__ort,1643569736.1652586,1643569736.2076447,0$0#]][__det,1643569736.20859,1643569738.931932,0$0#[__ort,1643569736.3555562,1643569738.8348587,0$0#]][__cls,1643569738.9405437,1643569739.24126,0$0#[__ort,1643569738.9429545,1643569739.0299811,0$0#][__ort,1643569739.0350616,1643569739.127901,0$0#][__ort,1643569739.132973,1643569739.2317488,0$0#][__ort,1643569739.2328234,1643569739.241071,0$0#]][__sty,1643569739.241476,1643569739.5114026,0$0#[__ort,1643569739.243572,1643569739.4119606,0$0#][__ort,1643569739.4144793,1643569739.4317007,0$0#][__ort,1643569739.4342513,1643569739.5082533,0$0#][__ort,1643569739.5091777,1643569739.5111573,0$0#]][__rec,1643569739.511604,1643569743.115833,0$0#[__ort,1643569739.5133343,1643569739.7487059,0$0#][__ort,1643569739.7528548,1643569740.0487385,0$0#][__ort,1643569740.1160934,1643569742.6137102,0$0#][__ort,1643569742.6292832,1643569743.1126142,0$0#]][__rec,1643569743.11609,1643569743.116233,0$0#][__det,1643569743.1164277,1643569743.1422083,0$0#[__ort,1643569743.1169982,1643569743.1402473,0$0#]][__det,1643569743.1426477,1643569743.1468668,0$0#[__ort,1643569743.143132,1643569743.145506,0$0#]][__det,1643569743.1472528,1643569743.2162328,0$0#[__ort,1643569743.1480312,1643569743.2121801,0$0#]][__det,1643569743.216631,1643569743.2421668,0$0#[__ort,1643569743.2174027,1643569743.2351496,0$0#]][__det,1643569743.242663,1643569743.2523344,0$0#[__ort,1643569743.2434154,1643569743.2501614,0$0#]][__det,1643569743.3165214,1643569743.329657,0$0#[__ort,1643569743.3176396,1643569743.3263106,0$0#]][__det,1643569743.3300874,1643569743.337189,0$0#[__ort,1643569743.330739,1643569743.3349724,0$0#]][__det,1643569743.337554,1643569743.342569,0$0#[__ort,1643569743.3380115,1643569743.3409102,0$0#]][__det,1643569743.3429003,1643569743.3468688,0$0#[__ort,1643569743.3433163,1643569743.345672,0$0#]][__det,1643569743.3472311,1643569743.3520138,0$0#[__ort,1643569743.3476806,1643569743.3503542,0$0#]][__det,1643569743.3524318,1643569743.3581665,0$0#[__ort,1643569743.3529246,1643569743.3563924,0$0#]][__det,1643569743.3585193,1643569743.4109883,0$0#[__ort,1643569743.3589113,1643569743.409384,0$0#]][__det,1643569743.411437,1643569743.4156177,0$0#[__ort,1643569743.4118354,1643569743.4143524,0$0#]][__det,1643569743.4159608,1643569743.420702,0$0#[__ort,1643569743.4164329,1643569743.418999,0$0#]][__det,1643569743.4210744,1643569743.4252756,0$0#[__ort,1643569743.4214988,1643569743.4240358,0$0#]][__det,1643569743.4256399,1643569743.4298625,0$0#[__ort,1643569743.426082,1643569743.4286163,0$0#]][__det,1643569743.4302363,1643569743.4343379,0$0#[__ort,1643569743.4306252,1643569743.433071,0$0#]][__det,1643569743.4346728,1643569743.4385982,0$0#[__ort,1643569743.435092,1643569743.4374073,0$0#]][__det,1643569743.4389238,1643569743.4435484,0$0#[__ort,1643569743.4393814,1643569743.4419074,0$0#]][__det,1643569743.4438791,1643569743.4482865,0$0#[__ort,1643569743.4443324,1643569743.4470842,0$0#]][__det,1643569743.4486613,1643569743.454831,0$0#[__ort,1643569743.4492812,1643569743.452746,0$0#]][__det,1643569743.4554029,1643569743.5328221,0$0#[__ort,1643569743.4574807,1643569743.5185628,0$0#]][__det,1643569743.5338244,1643569743.5492887,0$0#[__ort,1643569743.5352147,1643569743.5429738,0$0#]][__det,1643569743.5498576,1643569743.6286142,0$0#[__ort,1643569743.5520155,1643569743.618229,0$0#]][__det,1643569743.6297498,1643569743.7098956,0$0#[__ort,1643569743.632189,1643569743.6457608,0$0#]][__det,1643569743.710675,1643569743.733005,0$0#[__ort,1643569743.7126865,1643569743.7247958,0$0#]][__det,1643569743.7337465,1643569743.8100944,0$0#[__ort,1643569743.7356975,1643569743.7473083,0$0#]][__det,1643569743.8111055,1643569743.8347492,0$0#[__ort,1643569743.813039,1643569743.8244736,0$0#]][__det,1643569743.835479,1643569743.84312,0$0#[__ort,1643569743.836138,1643569743.8404937,0$0#]][__det,1643569743.843564,1643569743.8490357,0$0#[__ort,1643569743.844158,1643569743.8473823,0$0#]][__det,1643569743.8493845,1643569743.913976,0$0#[__ort,1643569743.8504245,1643569743.9103267,0$0#]][__det,1643569743.9145095,1643569743.9196005,0$0#[__ort,1643569743.9151065,1643569743.9183722,0$0#]][__det,1643569743.919938,1643569743.924156,0$0#[__ort,1643569743.9203613,1643569743.9229279,0$0#]][__det,1643569743.9244788,1643569743.9358187,0$0#[__ort,1643569743.9257007,1643569743.932356,0$0#]][__det,1643569743.9362285,1643569743.9403598,0$0#[__ort,1643569743.9366255,1643569743.939164,0$0#]][__det,1643569743.94068,1643569743.9454722,0$0#[__ort,1643569743.9411945,1643569743.9442341,0$0#]][__det,1643569743.9458015,1643569743.9520783,0$0#[__ort,1643569743.9464548,1643569743.9499493,0$0#]][__det,1643569743.9524298,1643569744.0121005,0$0#[__ort,1643569743.953075,1643569744.0093017,0$0#]][__det,1643569744.0125837,1643569744.0203052,0$0#[__ort,1643569744.0133524,1643569744.0177798,0$0#]]][__kvlayout,1643569744.15425,1643569745.3451543,0$0#[__ort,1643569744.1545331,1643569745.3447654,0$0#]][_ort_sess,1643569745.3523283,1643569745.6308331,0$0#][__tbl,1643569745.6312604,1643569745.9097774,0$0#[__ort,1643569745.6314573,1643569745.8510344,0$0#]]]]"""
    print(create_gantt_chart_time([tau]))
