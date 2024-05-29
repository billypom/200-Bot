import pykakasi
from korean_romanizer.romanizer import Romanizer


async def jp_kr_romanize(input):
    """Takes in east asian text - Returns romanized version"""
    r = Romanizer(input)
    kr_result = r.romanize()
    kks = pykakasi.kakasi()
    result = kks.convert(kr_result)
    my_string = ""
    for item in result:
        my_string += item["hepburn"]
    return my_string
