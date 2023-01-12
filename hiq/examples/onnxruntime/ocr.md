# HIQ + PaddleOCR ONNX

I found a python module for OCR task at: https://github.com/triwinds/ppocr-onnx.

I got the python script from there as below in `main.py`:

```
from ppocronnx.predict_system import TextSystem
import cv2

def main():
    text_sys = TextSystem()
    # 检测并识别文本
    img = cv2.imread('test.png')
    res = text_sys.detect_and_ocr(img)
    for boxed_result in res:
        print("{}, {:.3f}".format(boxed_result.ocr_text, boxed_result.score))

if __name__ == '__main__':
    main()
```

To get a performance report for this library, you just need to write a few line in `ocr_driver.py`:

```
import hiq
from hiq.framework.onnxruntime import OrtHiQLatency

driver = OrtHiQLatency(extra_metrics={hiq.ExtraMetrics.FILE})
hiq.mod("main").main()
driver.show()
```

Then run it and you can see the result:

```
❯ python ocr_driver.py
test_train_inference_python.sh, 0.947
results, 0.985
test_inference_cpp.sh, 0.993
log, 0.976
compare_results.py, 0.997
prepare.sh, 0.989
test_serving.sh, 0.940
test lite.sh, 0.962
精度是否对齐, 0.920
功能是否支持, 0.994

[2023-01-12 10:12:14.801197 - 10:12:15.996881]  [100.00%] 🟢_root_time(1.1957)
                                                            [OH:128078us]
[2023-01-12 10:12:14.801197 - 10:12:14.897981]  [  8.09%]    |_ort_session(0.0968) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/det/predict_det.py:63'})
[2023-01-12 10:12:14.805047 - 10:12:14.805075]  [  0.00%]    |  |___sess_init(0.0000) ({'file': '/Users/fuhwu/miniconda3/envs/gamma/lib/python3.8/site-packages/onnxruntime/capi/onnxruntime_inference_collection.py:304'})
[2023-01-12 10:12:14.805507 - 10:12:14.897944]  [  7.73%]    |  l___create_inference_session(0.0924) ({'file': '/Users/fuhwu/miniconda3/envs/gamma/lib/python3.8/site-packages/onnxruntime/capi/onnxruntime_inference_collection.py:324'})
[2023-01-12 10:12:14.906985 - 10:12:15.018793]  [  9.35%]    |_ort_session(0.1118) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/rec/predict_rec.py:43'})
[2023-01-12 10:12:14.907427 - 10:12:14.907441]  [  0.00%]    |  |___sess_init(0.0000) ({'file': '/Users/fuhwu/miniconda3/envs/gamma/lib/python3.8/site-packages/onnxruntime/capi/onnxruntime_inference_collection.py:304'})
[2023-01-12 10:12:14.907835 - 10:12:15.018746]  [  9.28%]    |  l___create_inference_session(0.1109) ({'file': '/Users/fuhwu/miniconda3/envs/gamma/lib/python3.8/site-packages/onnxruntime/capi/onnxruntime_inference_collection.py:324'})
[2023-01-12 10:12:15.077688 - 10:12:15.172866]  [  7.96%]    |_ort_session(0.0952) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/cls/predict_cls.py:38'})
[2023-01-12 10:12:15.082765 - 10:12:15.082883]  [  0.01%]    |  |___sess_init(0.0001) ({'file': '/Users/fuhwu/miniconda3/envs/gamma/lib/python3.8/site-packages/onnxruntime/capi/onnxruntime_inference_collection.py:304'})
[2023-01-12 10:12:15.086687 - 10:12:15.172820]  [  7.20%]    |  l___create_inference_session(0.0861) ({'file': '/Users/fuhwu/miniconda3/envs/gamma/lib/python3.8/site-packages/onnxruntime/capi/onnxruntime_inference_collection.py:324'})
[2023-01-12 10:12:15.426327 - 10:12:15.828819]  [ 33.66%]    |___ort_run(0.4025) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/det/predict_det.py:139'})
[2023-01-12 10:12:15.874985 - 10:12:15.879516]  [  0.38%]    |___ort_run(0.0045) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/cls/predict_cls.py:93'})
[2023-01-12 10:12:15.880639 - 10:12:15.884129]  [  0.29%]    |___ort_run(0.0035) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/cls/predict_cls.py:93'})
[2023-01-12 10:12:15.885680 - 10:12:15.936540]  [  4.25%]    |___ort_run(0.0509) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/rec/predict_rec.py:103'})
[2023-01-12 10:12:15.940034 - 10:12:15.996881]  [  4.75%]    l___ort_run(0.0568) ({'file': '/Users/fuhwu/ppocr-onnx/ppocronnx/rec/predict_rec.py:103'})
```

