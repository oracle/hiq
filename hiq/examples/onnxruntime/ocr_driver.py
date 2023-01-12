import hiq
from hiq.framework.onnxruntime import OrtHiQLatency

driver = OrtHiQLatency(extra_metrics={hiq.ExtraMetrics.FILE})
hiq.mod("main").main()
driver.show()
