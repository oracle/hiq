import hiq
from hiq.framework.onnxruntime import OrtHiQLatency


class MyFastAPI(hiq.HiQFastAPILatencyMixin, OrtHiQLatency):

    def custom(self):
        @self.inserter
        def predict(request) -> int:
            return self.o_predict(request)

        self.o_predict = hiq.mod("webapp")._predict
        hiq.mod("webapp")._predict = predict

        OrtHiQLatency.custom(self)

    def custom_disable(self):
        hiq.mod("webapp")._predict = self.o_predict
        OrtHiQLatency.custom_disable(self)


hiq.run_fastapi(app=hiq.mod("webapp").app, driver=MyFastAPI())
