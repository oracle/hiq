import os
import time
from typing import *

import hiq
from hiq import read_file
from hiq.memory import get_memory_mb
from hiq.hiq_utils import (
    func_args_handler,
    get_tau_id,
)
from hiq.utils import get_env_int, get_env_bool

LATENCY = "latency_us"
NODE = "node"
OPERATOR = "operator"

FIG_LAYOUT_1_3 = {
    "left": 0.06,
    "right": 0.99,
    "top": 0.90,
    "bottom": 0.05,
    "wspace": 0.4,
}

# Quant
QUANT_NONE = ""
QUANT_INT8 = "int8"
QUANT_FP16 = "fp16"
QUANT_BF16 = "bf16"
QUANT_FP32 = "fp32"
QUANT_TYPES = [QUANT_INT8, QUANT_FP16, QUANT_BF16, QUANT_FP32]

MODEL_NAME_PATTERN_ONNX = r"model([\w|\.]*?)\.onnx$"

TAU_ORT = "onnxruntime.capi.onnxruntime_inference_collection"

TAU_TBL_ORT = [
    (TAU_ORT, "Session", "run", "ort_run"),
    (TAU_ORT, "Session", "__init__", "sess_init"),
    (TAU_ORT, "Session", "run_with_ort_values", "run_with_ort_values"),
    (TAU_ORT, "Session", "run_with_iobinding", "run_with_iobinding"),
    (
        TAU_ORT,
        "InferenceSession",
        "_create_inference_session",
        "create_inference_session",
    ),
    (TAU_ORT, "InferenceSession", "_reset_session", "reset_session"),
]


def get_ort_session(sess_options):
    import onnxruntime as ort

    sess_options = sess_options or ort.SessionOptions()
    if "HIQ_ORT_INTRA_OPS_THREAD" in os.environ:
        sess_options.intra_op_num_threads = get_env_int("HIQ_ORT_INTRA_OPS_THREAD")
    if "HIQ_PROFILE" in os.environ:
        sess_options.enable_profiling = get_env_bool("HIQ_PROFILE")
    if "HIQ_PROFILE_PREFIX" in os.environ:
        sess_options.profile_file_prefix = get_env_bool("HIQ_PROFILE_PREFIX")
    return sess_options


class OrtHiQLatency(hiq.HiQSimple):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        extra_hiq_table += TAU_TBL_ORT
        hiq.HiQSimple.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=hiq_id_func,
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )

    def custom(s):
        s.o_ort_session = hiq.mod(TAU_ORT).InferenceSession.__init__

        @s.inserter
        def ort_session(
            self,
            path_or_bytes,
            sess_options=None,
            providers=None,
            provider_options=None,
        ):
            return s.o_ort_session(
                self,
                path_or_bytes,
                get_ort_session(sess_options),
                providers,
                provider_options,
            )

        hiq.mod(TAU_ORT).InferenceSession.__init__ = ort_session

    def custom_disable(s):
        hiq.mod(TAU_ORT).InferenceSession.__init__ = s.o_ort_session


class OrtHiQMemory(hiq.HiQMemory):
    def __init__(
        sf,
        hiq_table_or_path: Union[str, list] = [],
        metric_funcs: List[Callable] = [time.time, get_memory_mb],
        hiq_id_func: Callable = get_tau_id,
        func_args_handler: Callable = func_args_handler,
        target_path=None,
        max_hiq_size=30,
        verbose=False,
        fast_fail=True,
        tpl=None,
        extra_hiq_table=[],
        attach_timestamp=False,
        extra_metrics=set(),
        lmk_path=None,
        lmk_handler=None,
        lmk_logger=None,
    ):
        extra_hiq_table += TAU_TBL_ORT
        hiq.HiQSimple.__init__(
            sf,
            hiq_table_or_path=hiq_table_or_path,
            metric_funcs=metric_funcs,
            hiq_id_func=hiq_id_func,
            func_args_handler=func_args_handler,
            target_path=target_path,
            max_hiq_size=max_hiq_size,
            verbose=verbose,
            fast_fail=fast_fail,
            tpl=tpl,
            extra_hiq_table=extra_hiq_table,
            attach_timestamp=attach_timestamp,
            extra_metrics=extra_metrics,
            lmk_path=lmk_path,
            lmk_handler=lmk_handler,
            lmk_logger=lmk_logger,
        )

    def custom(s):
        s.o_ort_session = hiq.mod(TAU_ORT).InferenceSession.__init__

        @s.inserter
        def ort_session(
            self,
            path_or_bytes,
            sess_options=None,
            providers=None,
            provider_options=None,
        ):
            return s.o_ort_session(
                self,
                path_or_bytes,
                get_ort_session(sess_options),
                providers,
                provider_options,
            )

        hiq.mod(TAU_ORT).InferenceSession.__init__ = ort_session

    def custom_disable(s):
        hiq.mod(TAU_ORT).InferenceSession.__init__ = s.o_ort_session


################################ Plot ########################################
def file_size_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)


def get_model_name_from_path(s: str) -> str:
    tmp = s.split("/")
    # if input is yolo.pt, yolo is model name
    if len(tmp) == 1:
        if "." not in s:
            return s
        return s.split(".")[0]
    # aaa/bbb.pdmodel => bbb is the model name
    if "." in tmp[-1]:
        x = tmp[-1].split(".")[0]
        if x != "model":
            return x
    if len(tmp) <= 1:
        print("🦉 warning: NO model name")
        return ""
    if "mbin" in tmp[-2]:
        if len(tmp) < 3:
            print("🦉 code structure error")
            return ""
        return tmp[-3]
    return tmp[-2]


def get_qtype_from_onnx_path(onnx_path):
    """deduce quant type from onnx file path
    In Gamma, the file should be model.onnx, or model.int8.onnx...
    if None, it means this is not an onnx file
    """
    import re

    onnx_path = onnx_path.lower()
    print(f"model onnx_path: {onnx_path}")
    matches = re.finditer(MODEL_NAME_PATTERN_ONNX, onnx_path, re.MULTILINE)
    for _, match in enumerate(matches, start=1):
        for groupNum in range(0, len(match.groups())):
            groupNum = groupNum + 1
            qtype = match.group(groupNum)[1:]
            if qtype == "":
                qtype = QUANT_FP32
            if qtype not in QUANT_TYPES:
                raise ValueError(f"wrong qtype: {qtype}")
            return qtype
    return None


def plot_ort_profile(
    prof_file, model_path="", debug=False, style="ggplot", overwrite=True, topk=5
) -> List[List[str]]:
    import pandas as pd

    if os.path.exists(prof_file):
        js = read_file(prof_file, as_json=True)
        df = pd.DataFrame(process_onnx_profiling_output(js))
        mapping = {"args_op_name": OPERATOR, "dur": LATENCY, "name": NODE}
        df.rename(columns=mapping, inplace=True)
        csv_file = prof_file.replace(".json", ".csv")
        df.to_csv(csv_file)

        fig_name = prof_file.replace(".json", ".png")
        if debug:
            print(df.head(3))
            print(f"prof_file: {prof_file}")
            print(f"fig_name: {fig_name}")

        total_latency = df[df.cat == "Node"][LATENCY].sum()
        if model_path:
            model_name = get_model_name_from_path(model_path) if model_path else "Model"
            qtype = get_qtype_from_onnx_path(model_path) if model_path else "NA"
            fsize_str = (
                file_size_fmt(os.path.getsize(model_path)) if model_path else "NA"
            )
            title = f"Model: {model_name} ({qtype.upper()},{fsize_str}, node latency:{total_latency}us)"
        else:
            title = f"Model (node latency:{total_latency}us)"
        [fig_names, top_ops] = draw_onnx_profiling(
            df, fig_name, style=style, title=title, topk=topk
        )
        return [fig_names, top_ops, csv_file]
    return []


def process_onnx_profiling_output(js: dict) -> List[str]:
    rows = []
    for row in js:
        if "args" in row and isinstance(row["args"], dict):
            for k, v in row["args"].items():
                row["args_%s" % k] = v
            del row["args"]
        rows.append(row)
    return rows


# TODO: put this onnx profiling to ir utils package
def draw_onnx_profiling(
    df, fig_name, duration_lower_bound=50, style="ggplot", title=None, topk=5
) -> List[List[str]]:
    if OPERATOR not in df.columns.to_list():
        return ""

    import matplotlib.pyplot as plt

    print(df.columns.to_list())
    fig_names = []
    with plt.style.context(style):
        gr_dur = df[[LATENCY, OPERATOR]].groupby(OPERATOR).sum().sort_values(LATENCY)
        gr_n = df[[LATENCY, OPERATOR]].groupby(OPERATOR).count().sort_values(LATENCY)
        gr_n = gr_n.loc[gr_dur.index, :]

        fig, ax = plt.subplots(
            1, 3, figsize=(30, 10), gridspec_kw={"width_ratios": [2, 3, 4]}
        )
        if title:
            fig.suptitle(title, fontweight="extra bold")
        fig.tight_layout()

        gr_dur.plot.barh(ax=ax[0], grid=True)
        # print(f"gr_dur: {gr_dur}")
        gr_n.plot.barh(ax=ax[1], grid=True)
        ax[0].set_title("Operators by total duration(us)")
        ax[1].set_title("Operators & Occurrences")

        top_ops = gr_dur.index.values[-topk:].tolist()
        top_ops.reverse()
        # print(top_ops)
        gr2 = (
            df.loc[
                (df.operator.isin(top_ops)) & (df[LATENCY] > duration_lower_bound),
                [LATENCY, NODE],
            ]
            .groupby(NODE)
            .sum()
            .sort_values(LATENCY)
        )
        # print(gr2)
        gr2.tail(20).plot.barh(
            ax=ax[2],
            grid=True,
            title=f"Top 20 nodes of top 5 operators by latency > {duration_lower_bound}us",
        )
        plt.subplots_adjust(**FIG_LAYOUT_1_3)
        plt.savefig(fig_name)
        fig_names.append(fig_name)
    return [fig_names, top_ops]


if __name__ == "__main__":
    p = "/media/henry/wendy/git.repo/onnxruntime/gme_play/onnxruntime_profile__2023-01-05_16-10-58.json"
    plot_ort_profile(p)
