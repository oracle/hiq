import hiq
from hiq.framework.onnxruntime import OrtHiQLatency

driver = OrtHiQLatency()
hiq.mod("main").main()
driver.show()
