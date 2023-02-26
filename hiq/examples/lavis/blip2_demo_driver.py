import hiq


def run_main():
    driver = hiq.HiQTransformerGPUMemory(
        hiq_table_or_path=[
            ["lavis.models.blip2_models.blip2_t5","Blip2T5","from_pretrained","from_pretrained"],
            ["lavis.models","","load_model_and_preprocess", 'load_model_and_preprocess'],
            ["demo","","main","main"],
            ["lavis.models.blip2_models.modeling_t5","T5ForConditionalGeneration","forward","m_t5"],
            ["lavis.models.blip2_models.blip2_t5","Blip2T5","generate","Blip2T5_gen"],
            ##["lavis.models.blip2_models.blip2_t5","Blip2T5","forward","b2t5_fwd"],
            ["lavis.models.blip2_models.blip2_qformer","Blip2Qformer","generate","b2qf_gen"],
            ##["lavis.models.blip2_models.blip2_qformer","Blip2Qformer","forward","b2qf_fwd"],
            ["lavis.models.blip2_models.blip2_opt","Blip2OPT","generate","b2opt_gen"],
            ##["lavis.models.blip2_models.blip2_opt","Blip2OPT","forward","b2opt_fwd"],
            ["lavis.models.blip2_models.Qformer","BertEmbeddings","forward","Qformer_bembed"],
            ["lavis.models.blip2_models.Qformer","BertSelfAttention","forward","Qformer_sa"],
            ["lavis.models.blip2_models.Qformer","BertAttention","forward","Qformer_a"],
            ["lavis.models.blip2_models.Qformer","BertLayer","forward","Qformer_bl"],
            ["lavis.models.blip2_models.Qformer","BertEncoder","forward","Qformer_be"],
            ["lavis.models.blip2_models.Qformer","BertModel","forward","Qformer_bm"],
            ["lavis.models.blip2_models.Qformer","BertLMHeadModel","forward","Qformer_blmm"],
            ["transformers.generation.utils","GenerationMixin","beam_search","beam_search"]
            ##["lavis.models.base_model","BaseModel","from_pretrained", 'fped'],
        ]
    )
    hiq.mod("blip2_demo").main()
    driver.show()


if __name__ == "__main__":
    run_main()

