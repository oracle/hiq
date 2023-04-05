import time
import torch
from PIL import Image


def main():
    # setup device to use
    device = torch.device("cuda") if torch.cuda.is_available() else "cpu"

    from lavis.models import load_model_and_preprocess

    # loads BLIP-2 pre-trained model
    model, vis_processors, _ = load_model_and_preprocess(
        name="blip2_t5", model_type="pretrain_flant5xl", is_eval=True, device=device
    )
    model = model.half()

    # load sample image
    raw_image = Image.open("merlion.png").convert("RGB")
    # prepare the image
    image = vis_processors["eval"](raw_image).unsqueeze(0).to(device)
    prompt = "Question: which city is this? Answer:"
    answer = model.generate({"image": image, "prompt": prompt})
    print(answer)


if __name__ == "__main__":
    main()
