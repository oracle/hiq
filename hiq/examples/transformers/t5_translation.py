from transformers import pipeline, AutoConfig
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)


def translate():
    config = AutoConfig.from_pretrained("t5-small", device="cuda")
    translator = pipeline(
        "text2text-generation",
        model="t5-small",
        config=config,
        device=0,  # specify the GPU device number to use
    )
    result = translator(
        "translate English to French: Hello, how are you?", max_length=50
    )[0]["generated_text"]
    print(result)


if __name__ == "__main__":
    translate()
    """
    import cProfile
    with cProfile.Profile() as pr:
        translate()
        pr.dump_stats("translate.result.pstat")
    """
