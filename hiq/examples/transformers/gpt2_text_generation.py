from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig
import torch


def generate_text():
    """https://huggingface.co/docs/transformers/model_doc/gpt2"""
    # Load a pre-trained language model and tokenizer
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Configure generation parameters using a GenerationConfig object
    gen_config = GenerationConfig(
        max_new_tokens=50,
        num_beams=5,
        no_repeat_ngram_size=2,
        do_sample=True,
        temperature=0.7,
    )

    # Generate text using the generate method of the language model
    input_text = "The quick brown fox"
    input_ids = tokenizer.encode(input_text, return_tensors="pt").to(device)
    output_ids = model.generate(input_ids=input_ids, generation_config=gen_config)
    output_text = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    print(output_text)


if __name__ == "__main__":
    import cProfile

    with cProfile.Profile() as pr:
        generate_text()
        pr.dump_stats("text_generation.result.pstat")
