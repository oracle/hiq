import torch
import uvicorn
import os
#import onnxruntime as ort
#import numpy as np
from PIL import Image
from fastapi import FastAPI, Request, Cookie, Depends, Response
from fastapi import File, UploadFile
from lavis.models import load_model_and_preprocess

here = os.path.dirname(os.path.realpath(__file__))

def bfloat16_supported(device_type='cuda'):
  import torch
  try:
    with torch.amp.autocast(device_type=device_type, dtype=torch.bfloat16):
      pass
    return True
  except:
    return False


class Blip2Inference:
    def __init__(self) -> None:
      from collections import deque
      self.context = deque(maxlen=10)
      # setup device to use
      self.device = torch.device("cuda") if torch.cuda.is_available() else "cpu"
      #display(raw_image.resize((596, 437)))

      self.model, self.vis_processors, _ = load_model_and_preprocess(
          name="blip2_t5",
          model_type="pretrain_flant5xl",
          is_eval=True,
          device=self.device)
      self.model = self.model.half()

    def predict(self, image: UploadFile=None, question="which city is this?"):
        prompt = ""
        if len(self.context)>0:
          if len(self.context)>5:
            self.context.popleft()
          template = "Question: {} Answer: {}."
          prompt = " ".join([template.format(q, a) for q,a in self.context])
        prompt += f" Question: {question} Answer:"
        print("prompt:", prompt)
        raw_image = Image.open(image.file).convert("RGB")
        image_data = self.vis_processors["eval"](raw_image).unsqueeze(0).to(self.device)
        answer = self.model.generate({"image": image_data, "prompt": prompt})
        self.context.append((question, answer[0]))
        return {"answer": answer[0]}
        # 'singapore'

b2 = None

# step 2: start model serving
app = FastAPI()

# expiry map
import cachetools
ttl_cache = cachetools.TTLCache(maxsize=128, ttl=10 * 60)



def _predict(image: UploadFile, question):
    global b2
    if b2 is None:
      b2 = Blip2Inference()
    answer = b2.predict(image, question)
    return answer

import uuid

def get_session(session_id: str = Cookie(None), response: Response=None):
    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(key="session_id", value=session_id)
    return {"session_id": session_id}

@app.post("/predict")
async def predict(image: UploadFile, question: str):
    return _predict(image, question)

@app.get("/start")
async def index(session: dict = Depends(get_session)):
    session_id = session["session_id"]
    return {"message": f"Session {session_id} created"}

@app.get("/")
async def predict(request: Request):
    return "OK"


if __name__ == "__main__":
    uvicorn.run("webapp:app", host="0.0.0.0", port=9090, reload=False, workers=1)

