import os
import hiq

here = os.path.dirname(os.path.realpath(__file__))

class PaddleHiQLatency(hiq.HiQMemory):
    def custom(s):
        s.o_paddle_run = hiq.mod('paddle.fluid.core_avx').PaddleInferPredictor.run

        @s.inserter
        def paddle_run(self) -> bool:
            return s.o_paddle_run(self)

        hiq.mod('paddle.fluid.core_avx').PaddleInferPredictor.run = paddle_run

    def custom_disable(s):
        hiq.mod('paddle.fluid.core_avx').PaddleInferPredictor.run = s.o_paddle_run


driver = PaddleHiQLatency(f"{here}/paddleocr.conf")
hiq.mod("main").main()
driver.show()
