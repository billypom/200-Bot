import pykakasi
from korean_romanizer.romanizer import Romanizer
import logging


async def jp_kr_romanize(input):
    """Takes in east asian text - Returns romanized version"""
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
