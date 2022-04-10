import hiq
from hiq.framework.onnxruntime import OrtHiQMemory

driver = OrtHiQMemory()
hiq.mod("main").main()
driver.show()
