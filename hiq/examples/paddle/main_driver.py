import hiq
from hiq.framework.paddleocr import PaddleOcrHiQLatency

driver = PaddleOcrHiQLatency()
hiq.mod("main").main()
driver.show()
