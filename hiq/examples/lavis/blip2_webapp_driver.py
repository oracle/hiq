import hiq
from hiq.framework.onnxruntime import OrtHiQLatency

# export TOKENIZERS_PARALLELISM=false

hiq_table_or_path = [
    ["lavis.models.blip2_models.blip2_t5", "Blip2T5", "generate", "b2t5_gen"],
    ["lavis.models.blip2_models.blip2_t5", "Blip2T5", "forward", "b2t5_fwd"],
    ["lavis.models.blip2_models.blip2_qformer", "Blip2Qformer", "generate", "b2qf_gen"],
    ["lavis.models.blip2_models.blip2_qformer", "Blip2Qformer", "forward", "b2qf_fwd"],
    ["lavis.models.blip2_models.blip2_opt", "Blip2OPT", "generate", "b2opt_gen"],
    ["lavis.models.blip2_models.blip2_opt", "Blip2OPT", "forward", "b2opt_fwd"],
    ["lavis.models.blip2_models.Qformer", "BertEmbeddings", "forward", "qf_bembed"],
    ["lavis.models.blip2_models.Qformer", "BertSelfAttention", "forward", "qf_sa"],
    ["lavis.models.blip2_models.Qformer", "BertAttention", "forward", "qf_a"],
    ["lavis.models.blip2_models.Qformer", "BertLayer", "forward", "qf_bl"],
    ["lavis.models.blip2_models.Qformer", "BertEncoder", "forward", "qf_be"],
    ["lavis.models.blip2_models.Qformer", "BertModel", "forward", "qf_bm"],
    ["lavis.models.blip2_models.Qformer", "BertLMHeadModel", "forward", "qf_blmm"],
    ["transformers.generation.utils", "GenerationMixin", "beam_search", "bs"],
]


class MyFastAPI(hiq.HiQFastAPILatencyMixin, OrtHiQLatency):
    def __init__(self):
        super().__init__(
            hiq_table_or_path=hiq_table_or_path, extra_metrics={hiq.ExtraMetrics.ARGS}
        )

    def custom(self):
        @self.inserter
        def predict(image, question):
            return self.o_predict(image, question)

        self.o_predict = hiq.mod("webapp")._predict
        hiq.mod("webapp")._predict = predict

        OrtHiQLatency.custom(self)

    def custom_disable(self):
        hiq.mod("webapp")._predict = self.o_predict
        OrtHiQLatency.custom_disable(self)


hiq.run_fastapi(driver=MyFastAPI(), app=hiq.mod("webapp").app, port=9090)
