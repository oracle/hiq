import os

here = os.path.dirname(os.path.realpath(__file__))

with open(f"{here}/paddleocr.conf") as file:
    HIQ_PADDLEOCR_CONF = file.readlines()
