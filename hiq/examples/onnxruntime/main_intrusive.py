# https://pytorch.org/docs/stable/onnx.html
# https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

import os
import onnxruntime as ort
import numpy as np
from hiq.framework.onnxruntime import OrtHiQLatency
from hiq import ExtraMetrics, KEY_LATENCY

os.environ["LMK"] = "0"
driver = OrtHiQLatency(extra_metrics={ExtraMetrics.ARGS})

here = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(f"{here}/alexnet.onnx"):
    import torch
    import torchvision

    dummy_input = torch.randn(10, 3, 224, 224, device="cpu")
    model = torchvision.models.alexnet(pretrained=True)
    input_names = ["actual_input_1"] + ["learned_%d" % i for i in range(16)]
    output_names = ["output1"]
    _ = torch.onnx.export(
        model,
        dummy_input,
        f"{here}/alexnet.onnx",
        verbose=True,
        input_names=input_names,
        output_names=output_names,
    )
ort_session = ort.InferenceSession(f"{here}/alexnet.onnx")
for _ in range(3):
    _ = ort_session.run(
        None,
        {"actual_input_1": np.random.randn(10, 3, 224, 224).astype(np.float32)},
    )

driver.show()
t = driver.get_metrics(metrics_key=KEY_LATENCY)[0]
t.show()
t.to_img()
from hiq.utils import create_gantt_chart_time

create_gantt_chart_time([t.repr()])
