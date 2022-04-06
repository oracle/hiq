import hiq
from paddleocr import *
import paddle
import traceback
from inspect import currentframe as cf


class PaddleHiQLatency(hiq.HiQSimple):
    def custom(s):
        s.o_paddle_run = hiq.mod('paddle.fluid.core_avx').PaddleInferPredictor.run
        @s.inserter
        def paddle_run(self) -> bool:
            return s.o_paddle_run(self)
        hiq.mod('paddle.fluid.core_avx').PaddleInferPredictor.run = paddle_run

    def custom_disable(s):
        hiq.mod('paddle.fluid.core_avx').PaddleInferPredictor.run = s.o_paddle_run


# paddle.fluid.core_avx.PaddleInferPredictor.run
driver = PaddleHiQLatency(
    hiq_table_or_path=[
        # ["paddle.fluid.core_avx", "PaddleInferPredictor", "run", "run"],
        ["paddleocr", "", "draw_ocr", "draw_ocr"],
        ["paddleocr", "PaddleOCR", "__init__", "init"],
        ["paddleocr", "PaddleOCR", "ocr", "ocr"],
        ["paddleocr", "PaddleOCR", "__call__", "txt_model"],
        ["tools.infer.predict_det", "TextDetector", "__call__", "det_model"],
        ["tools.infer.predict_rec", "TextRecognizer", "__call__", "rec_model"],
        ["tools.infer.predict_cls", "TextClassifier", "__call__", "cls_model"],
        ["tools.infer.utility", "", "create_predictor", "create_predictor"],
        ["main", "", "main", "main"],
        ["PIL.Image", "", "open", "pil_open"],
        ["PIL.Image", "Image", "save", "pil_save"],
    ]
)
hiq.mod("main").main()
driver.show()
