import hiq
from paddleocr import *
driver = hiq.HiQLatency(
    hiq_table_or_path=[
        ["paddleocr", "", "draw_ocr", "draw_ocr"],
        ["paddleocr", "PaddleOCR", "__init__", "init"],
        ["paddleocr", "PaddleOCR", "ocr", "ocr"],
        ["paddleocr", "PaddleOCR", "__call__", "txt_model"],
        ["tools.infer.predict_det", "TextDetector", "__call__", "det_model"],
        ["tools.infer.predict_rec", "TextRecognizer", "__call__", "rec_model"],
        ["tools.infer.predict_cls", "TextClassifier", "__call__", "cls_model"],
        ["main", "", "main", "main"],
        ["PIL.Image", "", "open", "pil_open"],
        ["PIL.Image", "Image", "save", "pil_save"],
    ]
)
hiq.mod("main").main()
driver.show()
