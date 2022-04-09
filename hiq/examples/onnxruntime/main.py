# https://pytorch.org/docs/stable/onnx.html

import os
import onnxruntime as ort
import numpy as np

here = os.path.dirname(os.path.realpath(__file__))

if not os.path.exists(f"{here}/alexnet.onnx"):
    import torch
    import torchvision

    dummy_input = torch.randn(10, 3, 224, 224, device="cpu")
    model = torchvision.models.alexnet(pretrained=True)
    input_names = [ "actual_input_1" ] + [ "learned_%d" % i for i in range(16) ]
    output_names = [ "output1" ]
    _ = torch.onnx.export(model,
                    dummy_input,
                    f"{here}/alexnet.onnx",
                    verbose=True,
                    input_names=input_names,
                    output_names=output_names)


ort_session = ort.InferenceSession("alexnet.onnx")
outputs = ort_session.run(
    None,
    {"actual_input_1": np.random.randn(10, 3, 224, 224).astype(np.float32)},
)
print(outputs[0])
