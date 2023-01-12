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
