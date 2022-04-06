import hiq
from hiq.framework.paddleocr import HIQ_PADDLEOCR_CONF
from hiq.framework.paddle import PaddleHiQMemory

driver = PaddleHiQMemory(HIQ_PADDLEOCR_CONF)
hiq.mod("main").main()
driver.show()
