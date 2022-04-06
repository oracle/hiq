import os
import hiq

here = os.path.dirname(os.path.realpath(__file__))

HIQ_PADDLEOCR_CONF = hiq.hiq_utils.read_csv_to_list(f"{here}/paddleocr.conf")
