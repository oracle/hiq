import hiq
from hiq.framework.paddleocr import HIQ_PADDLEOCR_CONF

driver = hiq.HiQLatency(HIQ_PADDLEOCR_CONF)
hiq.mod("main").main()
driver.show()
