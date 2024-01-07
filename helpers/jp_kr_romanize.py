import pykakasi
from korean_romanizer.romanizer import Romanizer
import logging


# Input: string
# Output: romanized jp/kr string
async def jp_kr_romanize(input):
    print('hello?')
    logging.info(f"jp_kr_romanize | input: {input}")
    r = Romanizer(input)
    logging.info(f"jp_kr_romanize | Romanizer(input) = {r}")
    kr_result = r.romanize()
    logging.info(f"jp_kr_romanize | kr_result = {kr_result}")
    kks = pykakasi.kakasi()
    logging.info(f"jp_kr_romanize | pykakasi.kakasi() = {kks}")
    result = kks.convert(kr_result)
    logging.info(f"jp_kr_romanize | kks.convert(kr_result) = {result}")
    my_string = ""
    for item in result:
        my_string += item["hepburn"]
    logging.info(f"jp_kr_romanize | return value: {my_string}")
    return my_string

# Notes
## 'module' object is not callable
# - Resolve this by changing the order of functions in __init__.py
# - Apparently order matters, so yay...
