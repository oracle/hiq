from fastapi import FastAPI, Request
import uvicorn

import os
import onnxruntime as ort
import numpy as np

# step 1: prepare onnx model
here = os.path.dirname(os.path.realpath(__file__))
model_path = f"{here}/alexnet.onnx"


def prepare_model(download_path):
    import torch
    import torchvision
    print(f"Downloading AlexNet to {download_path} and converting to onnx format ...")
    dummy_input = torch.randn(10, 3, 224, 224)
    model = torchvision.models.alexnet(pretrained=True)
    input_names = ["actual_input_1"] + ["learned_%d" % i for i in range(16)]
    output_names = ["output1"]
    torch.onnx.export(model, dummy_input, download_path, input_names=input_names, output_names=output_names)
    print(f"Model is ready now!")


if not os.path.exists(model_path):
    prepare_model(download_path=model_path)

ort_session = ort.InferenceSession(f"{here}/alexnet.onnx", providers=['CPUExecutionProvider'])

# step 2: start model serving
app = FastAPI()


def _predict(request):
    res = ort_session.run(
        None,
        {"actual_input_1": np.random.randn(10, 3, 224, 224).astype(np.float32)},
    )
    return {"result": str(res[0].shape)}


@app.get("/predict")
async def predict(request: Request):
    return _predict(request)


if __name__ == "__main__":
    uvicorn.run("webapp:app", host="0.0.0.0", port=8080, reload=True)
