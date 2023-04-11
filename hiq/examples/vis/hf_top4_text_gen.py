import re
import transformers

import requests
from bs4 import BeautifulSoup
from transformers import AutoModel
from hiq.vis import print_model
from gptq import avoid_tensor_modified

import logging
logging.getLogger("transformers").setLevel(logging.ERROR)


def list_models(sort_by, task=None):
    """Returns first page of results from available models on huggingface.co"""
    if task is None:
        url = f"https://huggingface.co/models?sort={sort_by}"
    else:
        url = f"https://huggingface.co/models?pipeline_tag={task}&sort={sort_by}"

    response = requests.get(url)
    soup = BeautifulSoup(response.content.decode("utf8"), features="html.parser")

    for model in soup.find_all("article"):
        parsed_text = [
            line.strip()
            for line in re.sub(
                " +",
                " ",
                model.text.replace("\n", " ").replace("\t", " ").replace("•", "\n"),
            )
            .strip()
            .split("\n")
        ]
        model_name_str, last_updated_str, downloaded, *liked = parsed_text
        liked = int(liked[0]) if liked else 0

        model_name = model.find("a").attrs["href"][1:]
        timestamp = model.find("time").attrs["datetime"]
        yield {
            "model_name": model_name,
            "last_updated": timestamp,
            "downloaded": downloaded.strip(),
            "liked": liked,
        }


task = "text-generation"
sort_by = "downloads"

avoid_tensor_modified()
transformers.modeling_utils._init_weights = False

models={'bloom':0,'gpt':0,'opt':0}


c = 0
for i in list_models(sort_by, task=task):
    m = i["model_name"]
    sk = 0
    def xx(m):
      for n in models:
        if n in m.lower():
          models[n]+=1
          if models[n] > 1:
            return 0
          return 1

    if xx(m)==0:
      continue
    if c == 4:
        break
    try:
        model = AutoModel.from_pretrained(
            m, trust_remote_code=True, from_tf=False, from_flax=False
        )
        print(i)
        print_model(model, show_buffer=True)
    except:
        pass
    c += 1
