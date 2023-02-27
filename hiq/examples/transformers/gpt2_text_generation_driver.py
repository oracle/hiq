import hiq
from hiq.constants import HIQ_TABLE_SIO_RD, TAU_TABLE_DIO_RD, TAU_TABLE_NIO_GET
import time

def run_main():
    hiq_quadruple = [
        ##["torch", "", "matmul", "tr_matmul"],
        ##["torch", "", "multinomial", "tr_multinomial"],
        ["transformers", "AutoConfig", "from_pretrained", "from_pretrained"],
        ["transformers.generation.utils","GenerationMixin","beam_search","beam_search"],
        ["transformers.generation.utils","GenerationMixin","beam_sample","beam_sample"],
        ["transformers","GPT2TokenizerFast","encode","encode"],
        ["transformers","GPT2TokenizerFast","decode","decode"],
        ["transformers","GPT2LMHeadModel","generate","generate"],
        ["transformers","GPT2LMHeadModel","forward","gpt2_lmh_fwd"],
        ["transformers","GPT2Model","forward","gpt2_fwd"],
        ["transformers","GPT2DoubleHeadsModel","forward","gpt2_dhm_fwd"],
        #["transformers.models.gpt2.modeling_gpt2","GPT2Attention","forward","gpt2_att_fwd"],
        #["transformers.models.gpt2.modeling_gpt2","GPT2Block","forward","gpt2_blk_fwd"],
        #["transformers","BeamSearchScorer","process", "beam_score_proc"],
        ["transformers","BeamSearchScorer","finalize", "finalize"],
        ["torch", "", "load", "tr_load"],
    ]

    driver = hiq.HiQTransformerGPUMemory(
        hiq_table_or_path=hiq_quadruple,
        attach_timestamp=True,
        max_hiq_size=1,
        #extra_metrics={hiq.ExtraMetrics.ARGS},
        #extra_hiq_table=[TAU_TABLE_DIO_RD],
    )
    hiq.mod("gpt2_text_generation").generate_text()
    driver.show()


if __name__ == "__main__":
    run_main()
