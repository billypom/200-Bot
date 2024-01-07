import pykakasi
from korean_romanizer.romanizer import Romanizer
# Input: string
# Output: romanized jp/kr string
async def jp_kr_romanize(input):
    r = Romanizer(input)
    kr_result = r.romanize()
    kks = pykakasi.kakasi()
    result = kks.convert(kr_result)
    my_string = ""
    for item in result:
        my_string+=item['hepburn']
    return my_string